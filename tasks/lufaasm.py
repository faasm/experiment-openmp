from invoke import task
from os.path import join
import numpy as np
from os import makedirs, exists, listdir
import pprint
import requests
import time
import json

from tasks.faasm import (
    get_faasm_invoke_host_port,
    get_knative_headers,
)
from tasks.util import (
    RESULTS_DIR,
)

MAX_THREADS = 40

LULESH_USER = "lulesh"
LULESH_FUNC = "func"

LULESH_RESULTS_DIR = join(RESULTS_DIR, "lulesh")


def write_csv_header(result_file):
    makedirs(RESULTS_DIR, exist_ok=True)
    with open(result_file, "w") as out_file:
        out_file.write("Threads,Iteration,Actual,Reported\n")


def write_result_line(result_file, threads, iteration, actual, reported):
    with open(result_file, "a") as out_file:
        result_line = "{},{},{},{}\n".format(
            threads, iteration, actual, reported
        )
        out_file.write(result_line)


ITERATIONS = 50
CUBE_SIZE = 20
REGIONS = 11
BALANCE = 1
COST = 1


@task
def plot(ctx):
    # Get files
    filenames = listdir(LULESH_RESULTS_DIR)

    actuals = list()
    reporteds = list()
    errors = list()
    threads = list()

    for f in filenames:
        t = f.replace("lulesh_wasm_", "")
        t = t.replace(".csv", "")
        threads.append(int(t))

        # Read in the file
        file_path = join(LULESH_RESULTS_DIR, f)
        a = list()
        r = list()
        with open(file_path, "r") as fh:
            for line in fh:
                if line.startswith("Threads"):
                    continue

                if not line.strip():
                    continue

                parts = line.split(",")
                a.append(float(parts[2]))
                r.append(float(parts[3]))

        errors.append(np.std(r))
        actuals.append(np.median(a))
        reporteds.append(np.median(r))



@task
def run(
    ctx,
    repeats=3,
    threads=None,
    resume=1,
):
    host, port = get_faasm_invoke_host_port()

    url = "http://{}:{}".format(host, port)

    if threads:
        threads_list = [threads]
    else:
        threads_list = range(int(resume), MAX_THREADS)

    if not exists(LULESH_RESULTS_DIR):
        makedirs(LULESH_RESULTS_DIR)

    # Run experiments
    for n_threads in threads_list:
        print("Running Lulesh with {} threads".format(n_threads))

        result_file = join(
            LULESH_RESULTS_DIR, "lulesh_wasm_{}.csv".format(n_threads)
        )
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
                "user": LULESH_USER,
                "function": LULESH_FUNC,
                "input_data": input_data,
                "cmdline": " ".join(cmdline),
                "async": True,
            }

            # Start timer
            start = time.time()

            # Invoke
            print("Posting to {}".format(url))
            pprint.pprint(msg)

            headers = get_knative_headers()
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
                    "user": LULESH_USER,
                    "function": LULESH_FUNC,
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
