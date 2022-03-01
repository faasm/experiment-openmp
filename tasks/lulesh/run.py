from invoke import task
from multiprocessing import cpu_count
from subprocess import run
from os.path import join
from os import makedirs
from os.path import exists
import pprint
import requests
import time
import json
import os
from copy import copy

from tasks.faasm import (
    get_faasm_invoke_host_port,
    get_knative_headers,
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


def write_result_line(result_file, threads, iteration, actual, reported):
    print("Writing result to {}".format(result_file))
    with open(result_file, "a") as out_file:
        result_line = "{},{},{},{}\n".format(
            threads, iteration, actual, reported
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

MESSAGE_TYPE_FLUSH = 3

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
    host, port = get_faasm_invoke_host_port()

    url = "http://{}:{}".format(host, port)

    threads_list = range(int(start), int(end), step)

    if not exists(RESULTS_DIR):
        makedirs(RESULTS_DIR)

    # Run experiments
    headers = get_knative_headers()
    for n_threads in threads_list:
        print("Running Lulesh with {} threads".format(n_threads))

        # Start with a flush
        print("Flushing")
        msg = {"type": MESSAGE_TYPE_FLUSH}
        response = requests.post(url, json=msg, headers=headers, timeout=None)

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

            # Start timer
            start = time.time()

            # Invoke
            print("Posting to {}".format(url))
            pprint.pprint(msg)

            response = requests.post(url, json=msg, headers=headers)

            if response.status_code != 200:
                print(
                    "Initial request failed: {}:\n{}".format(
                        response.status_code, response.text
                    )
                )
            print("Response: {}".format(response.text))

            msg_id = int(response.text.strip())
            print("Polling message {}".format(msg_id))

            while True:
                interval = 2
                time.sleep(interval)

                status_msg = {
                    "user": WASM_USER,
                    "function": WASM_FUNC,
                    "status": True,
                    "id": msg_id,
                }
                response = requests.post(
                    url,
                    json=status_msg,
                    headers=headers,
                )

                print(response.text)
                if response.text.startswith("RUNNING"):
                    continue
                elif response.text.startswith("FAILED"):
                    raise RuntimeError("Call failed")
                elif not response.text:
                    raise RuntimeError("Empty status response")
                else:
                    # Try to parse to json
                    result_data = json.loads(response.text)
                    output_data = result_data["output_data"]

                    actual_time = time.time() - start
                    if output_data.startswith("Run completed"):

                        # Parse to get reported
                        reported = output_data.split("Elapsed time         =")[
                            1
                        ]
                        reported = reported.strip()
                        reported = reported.split(" ")[0]

                        print(
                            "SUCCESS: reported {} actual {}".format(
                                reported, actual_time
                            )
                        )
                        break
                    else:
                        print(
                            "Unrecognised or failure response: {}".format(
                                response.text
                            )
                        )
                        break

            # Write output
            write_result_line(
                result_file, n_threads, run_idx, actual_time, reported
            )
