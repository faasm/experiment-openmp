#!/usr/bin/python3
import os
import re
import sys
from subprocess import check_output, STDOUT

COVID_SIM_BUILD_PATH = "/build/experiment/src/CovidSim"
PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SCRIPT_DIR = "{}/third-party/covid-sim/data".format(PROJ_ROOT)
COUNT_SETUP = False


def run_single(country, num_omp_threads):
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
    # print(_out)
    exec_times = re.findall("Model ran in ([0-9.]*) seconds", _out)
    if COUNT_SETUP:
        exec_times += re.findall("Model setup in ([0-9.]*) seconds", _out)
    total_time = sum([float(val) for val in exec_times])
    print(total_time)
    print("------------------------------------------")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Two positional arguments required: <country> and <num-threads>")
        sys.exit(1)
    run_single(sys.argv[1], int(sys.argv[2]))
