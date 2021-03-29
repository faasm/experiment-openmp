from invoke import task
import json
from multiprocessing import cpu_count
from numpy import linspace
from subprocess import check_output, run
from os.path import join
from tasks.util import RESULTS_DIR, COVID_DIR
import os
import re
import sys
from collections import defaultdict
from subprocess import check_output, STDOUT, CalledProcessError


COVID_SIM_BUILD_PATH = "/build/experiment/src/CovidSim"
DATA_DIR = join(COVID_DIR, "data")

IMAGE_NAME = "experiment-covid"
RESULTS_FILE = join(RESULTS_DIR, "covid_native.dat")

COUNTRY = "Malta"
NUM_CORES = cpu_count()
NUM_POINTS = 10
NUM_RUNS = 3


@task
def native(local=True):
    if not local:
        print("Remote not yet implemented")
        exit(1)

    times = defaultdict(list)

    print("OpenMP CovidSim Native Benchmark for {}".format(COUNTRY))

    for n_threads in range(NUM_CORES):
        print("Running with {} OpenMP threads".format(n_threads))

        for _ in range(NUM_RUNS):
            times[n_threads].append(run_single_src(COUNTRY, n_threads))

            print("Run {}/{} finished!".format(_ + 1, NUM_RUNS))

    print(times)

    with open(RESULTS_FILE, "w+") as out_file:
        json.dump(times, out_file)


def clean_duplicates(country):
    for f in [
        "/tmp/{}_pop_density.bin".format(country),
        "/tmp/Network_{}_T1_R3.0.bin".format(country),
    ]:
        try:
            os.remove(f)
        except FileNotFoundError:
            continue


def run_single_src(country, num_omp_threads):
    # Bit copied from the original source
    # Lists of places that need to be handled specially
    united_states = ["United_States"]
    canada = ["Canada"]
    usa_territories = [
        "Alaska",
        "Hawaii",
        "Guam",
        "Virgin_Islands_US",
        "Puerto_Rico",
        "American_Samoa",
    ]
    nigeria = ["Nigeria"]

    # Population density file in gziped form, text file, and binary file as
    # processed by CovidSim
    if country in united_states + canada:
        wpop_file_root = "usacan"
    elif country in usa_territories:
        wpop_file_root = "us_terr"
    elif country in nigeria:
        wpop_file_root = "nga_adm1"
    else:
        wpop_file_root = "eur"
    wpop_file = "wpop_{}.txt".format(wpop_file_root)
    # End of paraphrased bit

    # Prepare cmd
    _cmd = [
        COVID_SIM_BUILD_PATH,
        "/c:{}".format(num_omp_threads),
        "/A:{}/admin_units/{}_admin.txt".format(DATA_DIR, country),
        "/PP:{}/param_files/preUK_R0=2.0.txt".format(DATA_DIR),
        "/P:{}/param_files/p_NoInt.txt".format(DATA_DIR),
        "/O:/tmp/{}_NoInt_R0=3.0".format(country),
        "/D:/tmp/{}".format(wpop_file),
        "/M:/tmp/{}_pop_density.bin".format(country),
        "/S:/tmp/Network_{}_T1_R3.0.bin".format(country),
        "/R:1.5 98798150 729101 17389101 4797132",
    ]
    cmd = " ".join(_cmd)
    print(cmd)

    # Simulator complains if output files already exist, so we clean them
    clean_duplicates(country)

    # Run and check_output and handle errors
    try:
        _out = check_output(cmd, shell=True, stderr=STDOUT).decode("utf-8")
    except CalledProcessError as e:
        clean_duplicates(country)
        raise e

    print(_out)

    exec_times = re.findall("Model ran in ([0-9.]*) seconds", _out)
    setup_times = re.findall("Model setup in ([0-9.]*) seconds", _out)

    if len(setup_times) != len(exec_times):
        print("Error: Mismatch between setup and run times")
        sys.exit(1)

    for i in range(len(exec_times)):
        exec_times[i] = float(exec_times[i]) - float(setup_times[i])

    total_time = sum([float(val) for val in exec_times])
    print(total_time)
