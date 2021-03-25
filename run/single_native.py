#!/usr/bin/python3
import os
import re
import sys
from subprocess import check_output, STDOUT, CalledProcessError

COVID_SIM_BUILD_PATH = "/build/experiment/src/CovidSim"
PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SCRIPT_DIR = "{}/third-party/covid-sim/data".format(PROJ_ROOT)
DATA_DIR = SCRIPT_DIR
NOT_COUNT_SETUP = True


def run_single_python(country, num_omp_threads, debug):
    """
    Run a single run_sample execution
    """
    print("CovidSim single execution w/ parameters:")
    print("\t- BUILD_PATH: {}".format(COVID_SIM_BUILD_PATH))
    print("\t- SCRIPT_DIR: {}".format(SCRIPT_DIR))
    print("\t- Country: {}".format(country))
    print("\t- Num. OMP Threads: {}".format(num_omp_threads))

    # Prepare cmd
    _cmd = [
        "{}/run_sample.py".format(SCRIPT_DIR),
        country,
        "--covidsim {}".format(COVID_SIM_BUILD_PATH),
        "--threads {}".format(num_omp_threads),
        "--outputdir /tmp/",
    ]
    cmd = " ".join(_cmd)
    print(cmd)

    # Run and check_output
    _out = check_output(cmd, shell=True, stderr=STDOUT).decode("utf-8")
    if debug:
        print(_out)
    exec_times = re.findall("Model ran in ([0-9.]*) seconds", _out)
    if COUNT_SETUP:
        exec_times += re.findall("Model setup in ([0-9.]*) seconds", _out)
    total_time = sum([float(val) for val in exec_times])
    print(total_time)
    print("------------------------------------------")


def clean_duplicates(country):
    for f in [
        "/tmp/{}_pop_density.bin".format(country),
        "/tmp/Network_{}_T1_R3.0.bin".format(country),
    ]:
        try:
            os.remove(f)
        except FileNotFoundError:
            continue


"""
Example Command Line script for a no intervention simulation
    /build/experiment/src/CovidSim \
        /c:1 \
        /A:/code/experiment-covid/third-party/covid-sim/data/admin_units/Virgin_Islands_US_admin.txt \
        /PP:/code/experiment-covid/third-party/covid-sim/data/param_files/preUK_R0=2.0.txt \
        /P:/code/experiment-covid/third-party/covid-sim/data/param_files/p_NoInt.txt \
        /O:/tmp/Virgin_Islands_US_NoInt_R0=3.0 \
        /D:/tmp/wpop_us_terr.txt \
        /M:/tmp/Virgin_Islands_US_pop_density.bin \
        /S:/tmp/Network_Virgin_Islands_US_T1_R3.0.bin \
        /R:1.5 98798150 729101 17389101 4797132
"""


def run_single_src(country, num_omp_threads, debug):
    """
    Run a single run_sample execution
    """
    print("CovidSim single execution w/ parameters:")
    print("\t- BUILD_PATH: {}".format(COVID_SIM_BUILD_PATH))
    print("\t- SCRIPT_DIR: {}".format(SCRIPT_DIR))
    print("\t- Country: {}".format(country))
    print("\t- Num. OMP Threads: {}".format(num_omp_threads))

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
    if debug:
        print(_out)
    exec_times = re.findall("Model ran in ([0-9.]*) seconds", _out)
    if NOT_COUNT_SETUP:
        setup_times = re.findall("Model setup in ([0-9.]*) seconds", _out)
        if len(setup_times) != len(exec_times):
            print("Error: Mismatch between setup and run times")
            sys.exit(1)
        for i in range(len(exec_times)):
            exec_times[i] = float(exec_times[i]) - float(setup_times[i])
    total_time = sum([float(val) for val in exec_times])
    print(total_time)
    print("------------------------------------------")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Two positional arguments required: <country> and <num-threads> (and --debug)"
        )
        sys.exit(1)

    debug = (len(sys.argv) >= 4) and (sys.argv[3] == "--debug")
    run_single_src(sys.argv[1], int(sys.argv[2]), debug)
