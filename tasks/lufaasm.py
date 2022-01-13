from invoke import task
from os.path import join
import numpy as np
import matplotlib.pyplot as plt
from os import makedirs, listdir
from os.path import exists
import pprint
import requests
import time
import json

from tasks.faasm import (
    get_faasm_invoke_host_port,
    get_knative_headers,
)
from tasks.util import (
    EXPERIMENTS_BASE_DIR,
)

MAX_THREADS = 45

LULESH_USER = "lulesh"
LULESH_FUNC = "func"

LULESH_RESULTS_DIR = join(EXPERIMENTS_BASE_DIR, "results", "lulesh")
LULESH_PLOTS_DIR = join(EXPERIMENTS_BASE_DIR, "plots")
LULESH_PLOT_FILE = join(LULESH_PLOTS_DIR, "lulesh.png")


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


ITERATIONS = 50
CUBE_SIZE = 20
REGIONS = 11
BALANCE = 1
COST = 1

MESSAGE_TYPE_FLUSH = 3


@task
def plot(ctx, headless=False):
    if not exists(LULESH_PLOTS_DIR):
        makedirs(LULESH_PLOTS_DIR)

    filenames = listdir(LULESH_RESULTS_DIR)

    filenames.sort()

    results = list()
    for f in filenames:
        t = f.replace("lulesh_wasm_", "")
        t = t.replace(".csv", "")

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

        result = (int(t), np.median(a), np.median(r), np.median(r))
        results.append(result)

    results.sort(key=lambda x: x[0])
    for r in results:
        print("{} threads {}s".format(r[0], r[2]))

    x = [r[0] for r in results]
    y = [r[2] for r in results]
    e = [r[3] for r in results]
    plt.errorbar(x, y, yerr=e, label="Faabric")

    ax = plt.gca()
    ax.set_ylabel("Runtime (s)")

    plt.tight_layout()
    plt.savefig(LULESH_PLOT_FILE, format="png")

    if not headless:
        plt.show()


@task
def run(ctx, start=1, end=MAX_THREADS, repeats=2, step=3):
    host, port = get_faasm_invoke_host_port()

    url = "http://{}:{}".format(host, port)

    threads_list = range(int(start), int(end), step)

    if not exists(LULESH_RESULTS_DIR):
        makedirs(LULESH_RESULTS_DIR)

    # Run experiments
    headers = get_knative_headers()
    for n_threads in threads_list:
        print("Running Lulesh with {} threads".format(n_threads))

        # Start with a flush
        print("Flushing")
        msg = {"type": MESSAGE_TYPE_FLUSH}
        response = requests.post(url, json=msg, headers=headers, timeout=None)

        result_file = join(
            LULESH_RESULTS_DIR, "lulesh_wasm_{}.csv".format(n_threads)
        )

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
