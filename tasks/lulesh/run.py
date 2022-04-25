from invoke import task
from multiprocessing import cpu_count
from subprocess import run, PIPE
from os.path import join
from os import makedirs, remove
from os.path import exists
import time
import os
from copy import copy

from tasks.faasm import (
    invoke_and_await,
    faasm_flush,
)

from tasks.util import (
    RESULTS_DIR,
)

from tasks.lulesh.env import (
    NATIVE_BINARY,
    WASM_FUNC,
    WASM_USER,
)

MIN_THREADS = 2
MAX_THREADS_FAASM = 32
MAX_THREADS_NATIVE = cpu_count()

# Range is exclusive
NUM_THREADS_FAASM = range(MIN_THREADS, MAX_THREADS_FAASM, 2)
NUM_THREADS_NATIVE = range(MIN_THREADS, MAX_THREADS_NATIVE, 1)

# These are the parameters for the LULESH executable. See defaults at
# https://github.com/LLNL/LULESH/blob/master/lulesh.cc#L2681
# and translation from cmdline args at
# https://github.com/LLNL/LULESH/blob/master/lulesh_tuple.h#L565
ITERATIONS = 50
CUBE_SIZE = 20
REGIONS = 11
BALANCE = 1
COST = 1

NUM_REPEATS = 3


def init_result_file(file_name, clean):
    result_file = join(RESULTS_DIR, file_name)

    if not exists(RESULTS_DIR):
        makedirs(RESULTS_DIR)

    if exists(result_file) and clean:
        remove(result_file)

    if not exists(result_file):
        with open(result_file, "w") as out_file:
            out_file.write("Threads,Iteration,Actual,Reported\n")

    return result_file


def write_result_line(result_file, threads, iteration, actual_s, reported):
    print("Writing result to {}".format(result_file))
    with open(result_file, "a") as out_file:
        result_line = "{},{},{},{}\n".format(
            threads, iteration, actual_s, reported
        )

        print(result_line)
        out_file.write(result_line)


def get_reported_time(output_data):
    if output_data.startswith("Run completed"):
        # Parse to get reported
        reported = output_data.split("Elapsed time         =")[1]
        reported = reported.strip()
        reported = reported.split(" ")[0]

        return reported
    else:
        print("Unrecognised or failure response: {}".format(output_data))

        return None


@task
def native(ctx, repeats=NUM_REPEATS, threads=None, clean=False):
    """
    Run LULESH natively
    """
    result_file = init_result_file("lulesh_native.csv", clean)

    if threads:
        threads_list = [int(threads)]
    else:
        threads_list = NUM_THREADS_NATIVE

    print(
        "Running native LULESH with {} repeats on threads: {}".format(
            repeats, threads_list
        )
    )

    for n_threads in threads_list:
        for run_idx in range(repeats):
            print(
                "Run {}/{} with {} threads".format(
                    run_idx + 1, repeats, n_threads
                )
            )

            # Set number of threads with environment variable natively
            env = copy(os.environ)
            env["OMP_NUM_THREADS"] = str(n_threads)

            # Build up list of commandline args
            cmd = [
                NATIVE_BINARY,
                "-i {}".format(ITERATIONS),
                "-s {}".format(CUBE_SIZE),
                "-r {}".format(REGIONS),
                "-c {}".format(COST),
                "-b {}".format(BALANCE),
            ]

            cmd_string = " ".join(cmd)
            print(cmd_string)

            # Start timer and host stats collection
            start_time = time.time()
            res = run(
                cmd_string,
                check=True,
                shell=True,
                env=env,
                stdout=PIPE,
                stderr=PIPE,
            )
            end_time = time.time() - start_time

            # Get the output
            cmd_out = res.stdout.decode("utf-8")

            reported = get_reported_time(cmd_out)

            actual_s = end_time - start_time
            write_result_line(
                result_file, n_threads, run_idx, actual_s, reported
            )


@task
def faasm(ctx, threads=None, repeats=NUM_REPEATS, clean=False):
    """
    Run LULESH experiment on Faasm
    """
    result_file = init_result_file("lulesh_wasm.csv", clean)

    if threads:
        threads_list = [int(threads)]
    else:
        threads_list = NUM_THREADS_FAASM

    # Run experiments
    for n_threads in threads_list:
        print("Running Lulesh with {} threads".format(n_threads))

        # Start with a flush
        faasm_flush()

        for run_idx in range(repeats):
            cmdline = [
                "-i {}".format(ITERATIONS),
                "-s {}".format(CUBE_SIZE),
                "-r {}".format(REGIONS),
                "-c {}".format(COST),
                "-b {}".format(BALANCE),
            ]

            # Pass threads as input data
            input_data = "{}".format(n_threads)

            # Build message data
            msg = {
                "user": WASM_USER,
                "function": WASM_FUNC,
                "input_data": input_data,
                "cmdline": " ".join(cmdline),
                "async": True,
            }

            actual_s, output_data = invoke_and_await(WASM_USER, WASM_FUNC, msg)
            reported = get_reported_time(output_data)

            # Write output
            write_result_line(
                result_file, n_threads, run_idx, actual_s, reported
            )
