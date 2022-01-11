from subprocess import run
from invoke import task
import time
import requests
import os
from copy import copy

from multiprocessing import cpu_count
from os import makedirs
from os.path import exists, join
from shutil import rmtree
from subprocess import run

from tasks.faasm import get_faasm_upload_host_port

from tasks.util import (
    PROJ_ROOT,
    CMAKE_TOOLCHAIN_FILE,
    FAASM_WASM_DIR,
    RESULTS_DIR,
)

LULESH_NATIVE_BUILD_DIR = join(PROJ_ROOT, "build", "lulesh", "native")
LULESH_WASM_BUILD_DIR = join(PROJ_ROOT, "build", "lulesh", "wasm")
LULESH_DIR = join(PROJ_ROOT, "third-party", "lulesh")

NATIVE_BINARY = join(LULESH_NATIVE_BUILD_DIR, "lulesh2.0")
WASM_BINARY = join(LULESH_WASM_BUILD_DIR, "lulesh2.0")
WASM_USER = "lulesh"
WASM_FUNC = "func"

NUM_CORES = cpu_count()
NUM_REPEATS = 3

# These are the parameters for the LULESH executable. See defaults at
# https://github.com/LLNL/LULESH/blob/master/lulesh.cc#L2681
# and translation from cmdline args at
# https://github.com/LLNL/LULESH/blob/master/lulesh_tuple.h#L565
ITERATIONS = 9999999
CUBE_SIZE = 40
REGIONS = 11
BALANCE = 1
COST = 1


@task
def native(ctx, clean=False):
    """
    Compile LULESH natively
    """
    if clean and exists(LULESH_NATIVE_BUILD_DIR):
        rmtree(LULESH_NATIVE_BUILD_DIR)

    makedirs(LULESH_NATIVE_BUILD_DIR, exist_ok=True)

    cmake_cmd = [
        "cmake",
        "-G Ninja",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DWITH_MPI=FALSE",
        LULESH_DIR,
    ]

    run(
        " ".join(cmake_cmd),
        shell=True,
        check=True,
        cwd=LULESH_NATIVE_BUILD_DIR,
    )

    run(
        "cmake --build . --target all",
        shell=True,
        check=True,
        cwd=LULESH_NATIVE_BUILD_DIR,
    )


@task
def wasm(ctx, clean=False):
    """
    Compile LULESH to wasm
    """
    if clean and exists(LULESH_WASM_BUILD_DIR):
        rmtree(LULESH_WASM_BUILD_DIR)

    makedirs(LULESH_WASM_BUILD_DIR, exist_ok=True)

    cmake_cmd = [
        "cmake",
        "-GNinja",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DWITH_MPI=FALSE",
        "-DWITH_FAASM=TRUE",
        "-DCMAKE_TOOLCHAIN_FILE={}".format(CMAKE_TOOLCHAIN_FILE),
        LULESH_DIR,
    ]
    cmake_cmd_str = " ".join(cmake_cmd)

    run(cmake_cmd_str, shell=True, check=True, cwd=LULESH_WASM_BUILD_DIR)

    run(
        "cmake --build . --target all",
        shell=True,
        check=True,
        cwd=LULESH_WASM_BUILD_DIR,
    )

    # Also copy into place locally
    if exists(FAASM_WASM_DIR):
        target_dir = join(FAASM_WASM_DIR, WASM_USER, WASM_FUNC)
        makedirs(target_dir, exist_ok=True)
        target_file = join(target_dir, "function.wasm")
        run(
            "cp {} {}".format(WASM_BINARY, target_file), shell=True, check=True
        )
        print("Copied wasm into place at {}".format(target_file))


@task
def upload(ctx):
    host, port = get_faasm_upload_host_port()

    url = "http://{}:{}/f/{}/{}".format(host, port, WASM_USER, WASM_FUNC)
    response = requests.put(url, data=open(WASM_BINARY, "rb"))

    print("Response {}: {}".format(response.status_code, response.text))


@task
def run_native(
    ctx,
    repeats=NUM_REPEATS,
    threads=None,
    resume=1,
    reverse=False,
):
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
def upload(ctx):
    host, port = get_faasm_upload_host_port()

    url = "http://{}:{}/f/{}/{}".format(host, port, WASM_USER, WASM_FUNC)
    response = requests.put(url, data=open(WASM_BINARY, "rb"))

    print("Response {}: {}".format(response.status_code, response.text))
