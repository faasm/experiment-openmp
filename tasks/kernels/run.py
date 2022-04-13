from os.path import join
from copy import copy
import os
from subprocess import run

from invoke import task

from tasks.kernels.env import (
    KERNELS_NATIVE_DIR,
    KERNELS_FAASM_USER,
)
from tasks.faasm import (
    faasm_flush,
    invoke_and_await,
)

NUM_THREADS = [2, 4, 8, 16]

SPARSE_GRID_SIZE_2LOG = 10
SPARSE_GRID_SIZE = pow(2, SPARSE_GRID_SIZE_2LOG)

KERNELS_CMDLINE = {
    "dgemm": [400, 400],
    # dgemm: iterations, matrix order
    "nstream": [20000, 200000, 0],
    # nstream: iterations, vector length, offset
    "reduce": [40000, 20000],
    # reduce: iterations, vector length
    "stencil": [200, 5000],
    # stencil: iterations, array dimension
    "global": [5000, 250000],
    # global: iterations, scramble string length
    "p2p": [750, 10000, 1000],
    # p2p: iterations, 1st array dimension, 2nd array dimension
}


def get_cmdline_args(kernel_name, n_threads):
    n_threads = int(n_threads)
    cmdline = [n_threads]
    cmdline.extend(KERNELS_CMDLINE[kernel_name])

    if kernel_name == "global":
        # Round down to a multiple of the number of threads
        cmdline[-1] = cmdline[-1] - (cmdline[-1] % n_threads)

    return " ".join([str(c) for c in cmdline])


KERNELS_STATS = {
    "dgemm": ("Avg time (s)", "Rate (MFlops/s)"),
    "nstream": ("Avg time (s)", "Rate (MB/s)"),
    "reduce": ("Avg time (s)", "Rate (MFlops/s)"),
    "stencil": ("Avg time (s)", "Rate (MFlops/s)"),
    "global": ("time (s)", "Rate (synch/s)"),
    "p2p": ("Avg time (s)", "Rate (MFlops/s)"),
}

KERNELS_NATIVE_EXECUTABLES = {
    "dgemm": join(KERNELS_NATIVE_DIR, "OPENMP", "DGEMM", "dgemm"),
    "nstream": join(KERNELS_NATIVE_DIR, "OPENMP", "Nstream", "nstream"),
    "reduce": join(KERNELS_NATIVE_DIR, "OPENMP", "Reduce", "reduce"),
    "stencil": join(KERNELS_NATIVE_DIR, "OPENMP", "Stencil", "stencil"),
    "global": join(KERNELS_NATIVE_DIR, "OPENMP", "Synch_global", "global"),
    "p2p": join(KERNELS_NATIVE_DIR, "OPENMP", "Synch_p2p", "p2p"),
}


@task
def flush(ctx):
    faasm_flush()


@task
def faasm(ctx, repeats=1, threads=None, kernel=None):
    """
    Run kernel(s) in Faasm
    """
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

                invoke_and_await(KERNELS_FAASM_USER, kernel, msg)


@task
def native(ctx, repeats=1, threads=None, kernel=None):
    """
    Run kernel(s) natively
    """
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
                run(cmd, shell=True, check=True, env=env)
