from copy import copy
import os
import time
from os.path import exists, join
from os import makedirs
from subprocess import run, PIPE

from invoke import task

from tasks.util import RESULTS_DIR

from tasks.kernels.env import (
    KERNELS_FAASM_USER,
    KERNELS_CMDLINE,
    KERNELS_NATIVE_EXECUTABLES,
    KERNELS_STATS,
)

from tasks.faasm import (
    faasm_flush,
    invoke_and_await,
)

NUM_THREADS = [2, 4, 8, 16]

SPARSE_GRID_SIZE_2LOG = 10
SPARSE_GRID_SIZE = pow(2, SPARSE_GRID_SIZE_2LOG)


def get_cmdline_args(kernel_name, n_threads):
    n_threads = int(n_threads)
    cmdline = [n_threads]
    cmdline.extend(KERNELS_CMDLINE[kernel_name])

    if kernel_name == "global":
        # Round down to a multiple of the number of threads
        cmdline[-1] = cmdline[-1] - (cmdline[-1] % n_threads)

    return " ".join([str(c) for c in cmdline])


def init_result_file(is_wasm):
    if is_wasm:
        result_file = join(RESULTS_DIR, "kernels_wasm.csv")
    else:
        result_file = join(RESULTS_DIR, "kernels_native.csv")

    if not exists(RESULTS_DIR):
        makedirs(RESULTS_DIR)

    if not exists(result_file):
        with open(result_file, "w") as out_file:
            out_file.write("Kernel,Threads,Iteration,Actual,Reported\n")

    return result_file


def write_result_line(
    result_file, kernel, n_threads, run_num, actual_time, reported_time
):
    print("Writing result to {}".format(result_file))
    with open(result_file, "a") as out_file:
        result_line = "{},{},{},{},{}\n".format(
            kernel, n_threads, run_num, actual_time, reported_time
        )
        out_file.write(result_line)


def process_result(
    result_file, result_data, kernel, n_threads, run_num, measured_time
):
    stats = KERNELS_STATS.get(kernel)
    timing_stat = stats[0]

    stat_parts = result_data.split(timing_stat)
    stat_parts = [s for s in stat_parts if s.strip()]
    if len(stat_parts) < 2:
        print(
            "WARNING: Could not find timing {} for kernel {} in output".format(
                timing_stat, kernel
            )
        )
        return

    reported_time = stat_parts[-1].replace(":", "")
    reported_time = [s.strip() for s in reported_time.split(" ") if s.strip()]
    reported_time = reported_time[0]
    print("Got {} = {} for {}".format(timing_stat, reported_time, kernel))

    reported_time = float(reported_time)
    write_result_line(
        kernel, result_file, n_threads, run_num, measured_time, reported_time
    )


@task
def flush(ctx):
    """
    Flush the Faasm cluster
    """
    faasm_flush()


@task
def faasm(ctx, repeats=1, threads=None, kernel=None, verbose=False):
    """
    Run kernel(s) in Faasm
    """
    result_file = init_result_file(True)

    if threads:
        n_threads = [threads]
    else:
        n_threads = NUM_THREADS

    if kernel:
        kernels = [kernel]
    else:
        kernels = KERNELS_CMDLINE.keys()

    for kernel in kernels:
        for nt in n_threads:
            for run_num in range(repeats):
                faasm_flush()

                cmdline = get_cmdline_args(kernel, nt)
                msg = {
                    "user": KERNELS_FAASM_USER,
                    "function": kernel,
                    "cmdline": cmdline,
                    "async": True,
                }

                # Make the call
                start = time.time()
                output_data = invoke_and_await(KERNELS_FAASM_USER, kernel, msg)
                actual_time = time.time() - start

                if verbose:
                    print(output_data)

                # Write the result
                process_result(
                    result_file, output_data, kernel, nt, run_num, actual_time
                )


@task
def native(ctx, repeats=1, threads=None, kernel=None, verbose=False):
    """
    Run kernel(s) natively
    """
    result_file = init_result_file(False)

    if threads:
        n_threads = [threads]
    else:
        n_threads = NUM_THREADS

    if kernel:
        kernels = [kernel]
    else:
        kernels = KERNELS_CMDLINE.keys()

    for kernel in kernels:
        for nt in n_threads:
            for run_num in range(repeats):
                nt = str(nt)

                env = copy(os.environ)

                cmdline = get_cmdline_args(kernel, nt)
                executable = KERNELS_NATIVE_EXECUTABLES[kernel]

                cmd = "{} {}".format(executable, cmdline)

                start = time.time()
                res = run(
                    cmd,
                    shell=True,
                    check=True,
                    env=env,
                    stdout=PIPE,
                    stderr=PIPE,
                )
                actual_time = time.time() - start

                # Get the output
                cmd_out = res.stdout.decode("utf-8")

                if verbose:
                    print(cmd_out)

                # Write the result
                process_result(
                    result_file, cmd_out, kernel, nt, run_num, actual_time
                )
