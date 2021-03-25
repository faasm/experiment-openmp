#!/usr/bin/python3
import json
from multiprocessing import cpu_count
from numpy import linspace
from subprocess import check_output
import os

# Experiment information
IMAGE_NAME = "experiment-covid-native"
PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BASE_DIR = "{}/../..".format(PROJ_ROOT)
with open(os.path.join(BASE_DIR, "VERSION")) as version_file:
    VERSION = version_file.read().strip()
RESULTS_FILE = "{}/results/covid/covid_native.dat".format(BASE_DIR)

# Benchmark parameters
COUNTRY = "Malta"
NUM_CORES = cpu_count()
NUM_POINTS = 10
NUM_RUNS = 3


def benchmark():
    times = {}
    print("OpenMP CovidSim Native Benchmark for {}".format(COUNTRY))
    for _num_omp_threads in linspace(1, NUM_CORES, NUM_POINTS, dtype=int):
        num_omp_threads = int(_num_omp_threads)
        print("Running with {} OpenMP Threads".format(num_omp_threads))
        if num_omp_threads not in times:
            times[num_omp_threads] = []
        for _ in range(NUM_RUNS):
            times[num_omp_threads].append(_run_single_impl(COUNTRY, num_omp_threads))
            print("Run {}/{} finished!".format(_ + 1, NUM_RUNS))
    print(times)
    with open(RESULTS_FILE, "w+") as out_file:
        json.dump(times, out_file)


# TODO change when running in remote machine
def _run_single_impl(country, num_omp_threads):
    _docker_cmd = [
        "docker run --rm",
        "faasm/{}:{}".format(IMAGE_NAME, VERSION),
        country,
        str(num_omp_threads),
    ]

    docker_cmd = " ".join(_docker_cmd)
    _out = check_output(docker_cmd, shell=True).decode("utf-8")
    return float(_out.split("\n")[-3])


if __name__ == "__main__":
    benchmark()
