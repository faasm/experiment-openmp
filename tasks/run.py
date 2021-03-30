from invoke import task
from multiprocessing import cpu_count
from subprocess import run, PIPE, STDOUT
from os.path import join, exists
from tasks.util import RESULTS_DIR, COVID_DIR, NATIVE_BUILD_DIR
import os
import re

COVID_SIM_EXE = join(NATIVE_BUILD_DIR, "src", "CovidSim")
DATA_DIR = join(COVID_DIR, "data")

IMAGE_NAME = "experiment-covid"
RESULTS_FILE = join(RESULTS_DIR, "covid_native.csv")

DEFAULT_COUNTRY = "Malta"
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


@task
def native(local=True, country=DEFAULT_COUNTRY):
    """
    Runs the native experiment
    """
    if not local:
        print("Remote not yet implemented")
        exit(1)

    # Write header to results
    with open(RESULTS_FILE, "w") as out_file:
        out_file.write("Country,Threads,Run,Time(s)\n")

    # Run experiments
    for n_threads in range(1, NUM_CORES + 1):
        print("Running {} with {} threads".format(country, n_threads))

        for run_idx in range(NUM_REPEATS):
            this_time = run_country_sim(country, n_threads)
            print("Run {}: {}".format(run_idx, this_time))

            with open(RESULTS_FILE, "a") as out_file:
                result_line = "{},{},{},{}\n".format(
                    country, n_threads, run_idx, this_time
                )
                out_file.write(result_line)

            print("Run {}/{} finished!".format(run_idx, NUM_REPEATS))


def clean_duplicates(country):
    files = [
        "/tmp/{}_pop_density.bin".format(country),
        "/tmp/Network_{}_T1_R3.0.bin".format(country),
    ]

    for f in files:
        if exists(f):
            os.remove(f)


def run_country_sim(country, n_threads):
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

    # Prepare cmd
    cmd = [
        COVID_SIM_EXE,
        "/c:{}".format(n_threads),
        "/A:{}/admin_units/{}_admin.txt".format(DATA_DIR, country),
        "/PP:{}/param_files/preUK_R0=2.0.txt".format(DATA_DIR),
        "/P:{}/param_files/p_NoInt.txt".format(DATA_DIR),
        "/O:/tmp/{}_NoInt_R0=3.0".format(country),
        "/D:/{}/populations/{}".format(DATA_DIR, wpop_file),
        "/M:/tmp/{}_pop_density.bin".format(country),
        "/S:/tmp/Network_{}_T1_R3.0.bin".format(country),
        "/R:1.5 98798150 729101 17389101 4797132",
    ]
    cmd_str = " ".join(cmd)
    print(cmd_str)

    # Simulator complains if output files already exist, so we clean them
    clean_duplicates(country)

    # Run the command
    cmd_res = run(cmd_str, shell=True, check=True, stdout=PIPE, stderr=STDOUT)
    cmd_out = cmd_res.stdout.decode("utf-8")
    print(cmd_out)

    # Extract run/ setup times form output
    exec_times = re.findall("Model ran in ([0-9.]*) seconds", cmd_out)
    setup_times = re.findall("Model setup in ([0-9.]*) seconds", cmd_out)

    if len(setup_times) != len(exec_times):
        raise RuntimeError("Error: Mismatch between setup and run times")

    for i, (exec_time, setup_time) in enumerate(zip(exec_times, setup_times)):
        exec_times[i] = float(exec_time) - float(setup_time)

    total_time = sum(exec_times)
    print(
        "{} with {} threads took {:.2f}s".format(
            country, n_threads, total_time
        )
    )

    return total_time
