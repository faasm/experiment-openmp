from invoke import task
from multiprocessing import cpu_count
from subprocess import run
from os.path import join
from os import makedirs
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

MAX_THREADS = 45


def write_csv_header(result_file):
    with open(result_file, "w") as out_file:
        out_file.write("Threads,Iteration,Actual,Reported\n")


def write_result_line(result_file, threads, iteration, actual_ms, reported):
    print("Writing result to {}".format(result_file))
    with open(result_file, "a") as out_file:
        result_line = "{},{},{},{}\n".format(
            threads, iteration, actual_ms, reported
        )
        out_file.write(result_line)


# These are the parameters for the LULESH executable. See defaults at
# https://github.com/LLNL/LULESH/blob/master/lulesh.cc#L2681
# and translation from cmdline args at
# https://github.com/LLNL/LULESH/blob/master/lulesh_tuple.h#L565
ITERATIONS = 50
CUBE_SIZE = 20
REGIONS = 11
BALANCE = 1
COST = 1

NUM_CORES = cpu_count()
NUM_REPEATS = 3


@task
def native(
    ctx,
    repeats=NUM_REPEATS,
    threads=None,
    resume=1,
    reverse=False,
):
    """
    Run LULESH natively
    """
    if threads:
        threads_list = [int(threads)]
    else:
        threads_list = list(range(int(resume), NUM_CORES + 1))

    if reverse:
        threads_list.reverse()

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
            run(cmd_string, check=True, shell=True, env=env)

            end_time = time.time() - start_time

            print("{} threads finished. Time {}".format(n_threads, end_time))


@task
def faasm(ctx, start=1, end=MAX_THREADS, repeats=2, step=3):
    """
    Run LULESH experiment on Faasm
    """
    threads_list = range(int(start), int(end), step)

    if not exists(RESULTS_DIR):
        makedirs(RESULTS_DIR)

    # Run experiments
    for n_threads in threads_list:
        print("Running Lulesh with {} threads".format(n_threads))

        # Start with a flush
        faasm_flush()

        result_file = join(RESULTS_DIR, "lulesh_wasm_{}.csv".format(n_threads))

        if not exists(result_file):
            write_csv_header(result_file)

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

            if output_data.startswith("Run completed"):
                # Parse to get reported
                reported = output_data.split("Elapsed time         =")[1]
                reported = reported.strip()
                reported = reported.split(" ")[0]

                print(
                    "SUCCESS: reported {} actual {}s".format(
                        reported, actual_s
                    )
                )
                break
            else:
                print(
                    "Unrecognised or failure response: {}".format(output_data)
                )
                break

            # Write output
            write_result_line(
                result_file, n_threads, run_idx, actual_s, reported
            )
