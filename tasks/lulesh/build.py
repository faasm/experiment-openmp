from subprocess import run
from invoke import task
import requests

from os import makedirs
from os.path import exists, join
from shutil import rmtree

from tasks.faasm import get_faasm_upload_host_port

from tasks.util import (
    CMAKE_TOOLCHAIN_FILE,
    FAASM_WASM_DIR,
)

from tasks.lulesh.env import (
    LULESH_NATIVE_BUILD_DIR,
    LULESH_DIR,
    LULESH_WASM_BUILD_DIR,
    WASM_BINARY,
    WASM_FUNC,
    WASM_USER,
)


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
