from os.path import join
import time
from copy import copy
import os
from subprocess import run
import requests
from pprint import pprint

from invoke import task

from tasks.kernels.env import (
    KERNELS_NATIVE_DIR,
    KERNELS_FAASM_USER,
)
from tasks.faasm import (
    get_faasm_invoke_host_port,
    get_knative_headers,
    faasm_flush,
    invoke_and_await,
)

NUM_THREADS = [2, 4, 8, 16]

SPARSE_GRID_SIZE_2LOG = 10
SPARSE_GRID_SIZE = pow(2, SPARSE_GRID_SIZE_2LOG)

KERNELS_CMDLINE = {
    "dgemm": "400 400",
    # dgemm: iterations, matrix order
    "nstream": "2000000 200000 0",
    # nstream: iterations, vector length, offset
    "reduce": "40000 20000",
    # reduce: iterations, vector length
    "stencil": "20000 1000",
    # stencil: iterations, array dimension
    "global": "1000 10000",
    # global: iterations, scramble string length
    "p2p": "10000 10000 1000",
    # p2p: iterations, 1st array dimension, 2nd array dimension
}


KERNELS_NATIVE_EXECUTABLES = {
    "dgemm": join(KERNELS_NATIVE_DIR, "OPENMP", "DGEMM", "dgemm"),
    "nstream": join(KERNELS_NATIVE_DIR, "OPENMP", "Nstream", "nstream"),
    "random": join(KERNELS_NATIVE_DIR, "OPENMP", "Random", "random"),
    "reduce": join(KERNELS_NATIVE_DIR, "OPENMP", "Reduce", "reduce"),
    "stencil": join(KERNELS_NATIVE_DIR, "OPENMP", "Stencil", "stencil"),
    "sparse": join(KERNELS_NATIVE_DIR, "OPENMP", "Sparse", "sparse"),
    "global": join(KERNELS_NATIVE_DIR, "OPENMP", "Synch_global", "global"),
    "p2p": join(KERNELS_NATIVE_DIR, "OPENMP", "Synch_p2p", "p2p"),
}

KERNELS_STATS = {
    # "dgemm": ("Avg time (s)", "Rate (MFlops/s)"), uses MPI_Group_incl
    # "nstream": ("Avg time (s)", "Rate (MB/s)"),
    # "random": ("Rate (GUPS/s)", "Time (s)"), uses MPI_Alltoallv
    "reduce": ("Rate (MFlops/s)", "Avg time (s)"),
    "sparse": ("Rate (MFlops/s)", "Avg time (s)"),
    # "stencil": ("Rate (MFlops/s)", "Avg time (s)"),
    # "global": ("Rate (synch/s)", "time (s)"), uses MPI_Type_commit
    "p2p": ("Rate (MFlops/s)", "Avg time (s)"),
    "transpose": ("Rate (MB/s)", "Avg time (s)"),
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

    for k in kernels:
        for nt in n_threads:
            for run_num in range(repeats):
                faasm_flush()

                cmdline = "{} {}".format(nt, KERNELS_CMDLINE[k])
                msg = {
                    "user": KERNELS_FAASM_USER,
                    "function": k,
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

                cmdline = KERNELS_CMDLINE[kernel]
                executable = KERNELS_NATIVE_EXECUTABLES[kernel]

                cmd = "{} {} {}".format(executable, nt, cmdline)
                run(cmd, shell=True, check=True, env=env)
