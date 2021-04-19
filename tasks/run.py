from invoke import task
from multiprocessing import cpu_count
from subprocess import run, PIPE, STDOUT
from os.path import join, exists, dirname
from tasks.util import (
    RESULTS_DIR,
    COVID_DIR,
    NATIVE_BUILD_DIR,
    FAASM_USER,
    FAASM_FUNC,
)
from os import makedirs, remove
import requests
import re

COVID_SIM_EXE = join(NATIVE_BUILD_DIR, "src", "CovidSim")
DATA_DIR = join(COVID_DIR, "data")

FAASM_LOCAL_SHARED_DIR = "/usr/local/faasm/shared_store/covid"
FAASM_DATA_DIR = "faasm://covid"

IMAGE_NAME = "experiment-covid"

NATIVE_RESULTS_FILE = join(RESULTS_DIR, "covid_native.csv")
WASM_RESULTS_FILE = join(RESULTS_DIR, "covid_wasm.csv")

# Countries in order of size:
# - Guam
# - US Virgin Islands
# - Iceland
# - Malta
# - Alaska (quite longer)
DEFAULT_COUNTRY = "Guam"
NUM_CORES = cpu_count()
NUM_REPEATS = 3

# -----------------------------------
# Constants from the original source
UNITED_STATES = ["United_States"]
CANADA = ["Canada"]

USA_TERRITORIES = [
    "Alaska",
    "Hawaii",
    "Guam",
    "Virgin_Islands_US",
    "Puerto_Rico",
    "American_Samoa",
]

NIGERIA = ["Nigeria"]
# -----------------------------------


def get_wpop_filename(country):
    # Work out population file
    if country in UNITED_STATES + CANADA:
        wpop_file_root = "usacan"
    elif country in USA_TERRITORIES:
        wpop_file_root = "us_terr"
    elif country in NIGERIA:
        wpop_file_root = "nga_adm1"
    else:
        wpop_file_root = "eur"

    wpop_file = "wpop_{}.txt".format(wpop_file_root)
    return wpop_file


def get_data_files(country):
    """
    Lists data files that must be available to the application, with paths
    relative to the data dir
    """
    wpop_file = get_wpop_filename(country)

    files = [
        "admin_units/{}_admin.txt".format(country),
        "param_files/preUK_R0=2.0.txt",
        "param_files/p_NoInt.txt",
        "populations/{}".format(wpop_file),
    ]
    return files


def get_cmdline_args(country, n_threads, data_dir):
    wpop_file = get_wpop_filename(country)

    return [
        "/c:{}".format(n_threads),
        "/A:{}/admin_units/{}_admin.txt".format(data_dir, country),
        "/PP:{}/param_files/preUK_R0=2.0.txt".format(data_dir),
        "/P:{}/param_files/p_NoInt.txt".format(data_dir),
        "/O:/tmp/{}_NoInt_R0=3.0".format(country),
        "/D:/{}/populations/{}".format(data_dir, wpop_file),
        "/M:/tmp/{}_pop_density.bin".format(country),
        "/S:/tmp/Network_{}_T1_R3.0.bin".format(country),
        "/R:1.5 98798150 729101 17389101 4797132",
    ]


def write_csv_header(result_file):
    makedirs(RESULTS_DIR, exist_ok=True)
    with open(result_file, "w") as out_file:
        out_file.write("Country,Threads,Run,Time(s)\n")


def write_result_line(result_file, country, n_threads, run_idx, total_time):
    with open(result_file, "a") as out_file:
        result_line = "{},{},{},{}\n".format(
            country, n_threads, run_idx, total_time
        )
        out_file.write(result_line)


@task
def upload_data(
    ctx, local=True, host="faasm", port=8002, country=DEFAULT_COUNTRY
):
    """
    Uploads the data files needed for Covid sim
    """

    files = get_data_files(country)

    for relative_path in files:
        local_file_path = join(DATA_DIR, relative_path)

        if local:
            # Create directory if not exists
            dest_file = join(FAASM_LOCAL_SHARED_DIR, relative_path)
            dest_dir = dirname(dest_file)
            makedirs(dest_dir, exist_ok=True)

            # Do the copy. We use `cp` as the Python copyfile seems unreliable
            # with bigger files
            print("Copying {} -> {}".format(local_file_path, dest_file))
            run(
                "cp {} {}".format(local_file_path, dest_file),
                shell=True,
                check=True,
            )
        else:
            print("Uploading {} as a shared file".format(relative_path))
            url = "http://{}:{}/file"

            response = requests.put(
                url,
                data=open(local_file_path, "rb"),
                headers={"FilePath": relative_path},
            )

            print(
                "Response {}: {}".format(response.status_code, response.text)
            )


@task
def faasm(
    ctx, host="faasm", port=8080, country=DEFAULT_COUNTRY, repeats=NUM_REPEATS
):
    """
    Runs the faasm experiment
    """
    url = "http://{}:{}".format(host, port)

    write_csv_header(WASM_RESULTS_FILE)

    # Run experiments
    for n_threads in range(1, NUM_CORES + 1):
        print("Running {} with {} threads".format(country, n_threads))

        for run_idx in range(repeats):
            cmdline_args = get_cmdline_args(country, n_threads, FAASM_DATA_DIR)

            # Build message data
            msg = {
                "user": FAASM_USER,
                "function": FAASM_FUNC,
                "cmdline": " ".join(cmdline_args),
            }

            # Invoke
            response = requests.post(url, json=msg)
            print(
                "Response {}:\n{}".format(response.status_code, response.text)
            )

            # Write outputs
            total_time = parse_output(response.text)
            write_result_line(
                WASM_RESULTS_FILE, country, n_threads, run_idx, total_time
            )


@task
def native(
    ctx,
    local=True,
    country=DEFAULT_COUNTRY,
    debug=False,
    threads=None,
    repeats=NUM_REPEATS,
):
    """
    Runs the native experiment
    """
    if not local:
        print("Remote not yet implemented")
        exit(1)

    write_csv_header(NATIVE_RESULTS_FILE)

    if threads:
        threads_list = [threads]
    else:
        threads_list = range(1, NUM_CORES + 1)

    # Run experiments
    for n_threads in threads_list:
        print("Running {} with {} threads".format(country, n_threads))

        for run_idx in range(repeats):
            cmdline_args = get_cmdline_args(country, n_threads, DATA_DIR)

            # Prepare cmd
            cmd = [COVID_SIM_EXE]
            cmd.extend(cmdline_args)
            cmd_str = " ".join(cmd)
            print(cmd_str)

            # Simulator complains if output files already exist
            clean_duplicates(country)

            if debug:
                run(cmd_str, shell=True, check=True)
            else:
                # Run the command
                cmd_res = run(
                    cmd_str, shell=True, check=True, stdout=PIPE, stderr=STDOUT
                )
                cmd_out = cmd_res.stdout.decode("utf-8")

                # Parse the output
                this_time = parse_output(cmd_out)

                # Record the result
                write_result_line(
                    NATIVE_RESULTS_FILE, country, n_threads, run_idx, this_time
                )

                print(
                    "{} {} threads, run {}/{}: {}".format(
                        country, n_threads, run_idx, repeats, this_time
                    )
                )


def clean_duplicates(country):
    files = [
        "/tmp/{}_pop_density.bin".format(country),
        "/tmp/Network_{}_T1_R3.0.bin".format(country),
    ]

    for f in files:
        if exists(f):
            remove(f)


def parse_output(cmd_out):
    # Extract run/ setup times form output
    exec_times = re.findall("Model ran in ([0-9.]*) seconds", cmd_out)
    setup_times = re.findall("Model setup in ([0-9.]*) seconds", cmd_out)

    if len(setup_times) != len(exec_times):
        raise RuntimeError("Error: Mismatch between setup and run times")

    for i, (exec_time, setup_time) in enumerate(zip(exec_times, setup_times)):
        exec_times[i] = float(exec_time) - float(setup_time)

    total_time = sum(exec_times)

    return total_time
