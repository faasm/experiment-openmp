from invoke import task
from multiprocessing import cpu_count
from subprocess import run, PIPE, STDOUT
from os.path import join, dirname
from tasks.util import (
    RESULTS_DIR,
    COVID_DIR,
    NATIVE_BUILD_DIR,
    FAASM_USER,
    FAASM_FUNC,
)
from os import makedirs
import requests
import re
import time

COVID_SIM_EXE = join(NATIVE_BUILD_DIR, "src", "CovidSim")
DATA_DIR = join(COVID_DIR, "data")

FAASM_LOCAL_SHARED_DIR = "/usr/local/faasm/shared_store"
FAASM_DATA_DIR = "faasm://covid"

IMAGE_NAME = "experiment-covid"

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
        out_file.write("Country,Threads,Run,Setup,Execution,Actual\n")


def write_result_line(
    result_file,
    country,
    n_threads,
    run_idx,
    setup_time,
    exec_time,
    actual_time,
):
    with open(result_file, "a") as out_file:
        result_line = "{},{},{},{},{},{}\n".format(
            country,
            n_threads,
            run_idx,
            setup_time,
            exec_time,
            actual_time,
        )
        out_file.write(result_line)


@task
def upload_data(
    ctx, local=False, host="localhost", port=8002, country=DEFAULT_COUNTRY
):
    """
    Uploads the data files needed for Covid sim
    """

    files = get_data_files(country)

    for relative_path in files:
        local_file_path = join(DATA_DIR, relative_path)
        faasm_file_path = join("covid", relative_path)

        if local:
            # Create directory if not exists
            dest_file = join(FAASM_LOCAL_SHARED_DIR, faasm_file_path)
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
            print("Uploading {} as a shared file".format(faasm_file_path))
            url = "http://{}:{}/file".format(host, port)

            response = requests.put(
                url,
                data=open(local_file_path, "rb"),
                headers={"FilePath": faasm_file_path},
            )

            print(
                "Response {}: {}".format(response.status_code, response.text)
            )


@task
def faasm(
    ctx,
    host="localhost",
    port=8080,
    country=DEFAULT_COUNTRY,
    repeats=NUM_REPEATS,
    threads=None,
):
    """
    Runs the faasm experiment
    """
    url = "http://{}:{}".format(host, port)
    result_file = join(RESULTS_DIR, "covid_wasm_{}.csv".format(country))
    write_csv_header(result_file)

    if threads:
        threads_list = [threads]
    else:
        threads_list = range(1, NUM_CORES + 1)

    # Run experiments
    for n_threads in threads_list:
        print("Running {} with {} threads".format(country, n_threads))

        for run_idx in range(repeats):
            cmdline_args = get_cmdline_args(country, n_threads, FAASM_DATA_DIR)

            # Build message data
            msg = {
                "user": FAASM_USER,
                "function": FAASM_FUNC,
                "cmdline": " ".join(cmdline_args),
                "async": True,
            }

            # Invoke
            start = time.time()
            response = requests.post(url, json=msg)

            if response.status_code != 200:
                print(
                    "Initial request failed: {}:\n{}".format(
                        response.status_code, response.text
                    )
                )

            msg_id = int(response.text.strip())
            print("Polling message {}".format(msg_id))

            while True:
                interval = 2
                time.sleep(interval)

                status_msg = {
                    "user": "cov",
                    "function": "sim",
                    "status": True,
                    "id": msg_id,
                }
                response = requests.post(url, json=status_msg)

                print(response.text)
                if response.text.startswith("SUCCESS"):
                    actual_time = time.time() - start
                    break

                if response.text.startswith("FAILED"):
                    raise RuntimeError("Call failed")

            # Parse output
            setup_time, exec_time = parse_output(response.text)

            # Write output
            write_result_line(
                result_file,
                country,
                n_threads,
                run_idx,
                setup_time,
                exec_time,
                actual_time,
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

    result_file = join(RESULTS_DIR, "covid_native_{}.csv".format(country))
    write_csv_header(result_file)

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

            if debug:
                run(cmd_str, shell=True, check=True)
            else:
                # Run the command
                start = time.time()
                cmd_res = run(
                    cmd_str, shell=True, check=True, stdout=PIPE, stderr=STDOUT
                )
                actual_time = time.time() - start

                # Get the output
                cmd_out = cmd_res.stdout.decode("utf-8")

                # Parse the output
                setup_time, exec_time = parse_output(cmd_out)

                # Record the result
                write_result_line(
                    result_file,
                    country,
                    n_threads,
                    run_idx,
                    setup_time,
                    exec_time,
                    actual_time,
                )

                print(
                    "{} {} threads, run {}/{}: {}".format(
                        country, n_threads, run_idx, repeats, exec_time
                    )
                )


def parse_output(cmd_out):
    # Extract run/ setup times form output
    exec_times = re.findall("Model ran in ([0-9.]*) seconds", cmd_out)
    setup_times = re.findall("Model setup in ([0-9.]*) seconds", cmd_out)

    if len(setup_times) != 1:
        raise RuntimeError(
            "Expected to find one setup time but got {}".format(
                len(setup_times)
            )
        )

    if len(exec_times) != 1:
        raise RuntimeError(
            "Expected to find one execution time but got {}".format(
                len(exec_times)
            )
        )

    exec_time = float(exec_times[0])
    setup_time = float(setup_times[0])

    return setup_time, exec_time
