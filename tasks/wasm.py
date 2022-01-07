from invoke import task
import requests
from shutil import rmtree
from os.path import exists, join
from os import makedirs
from subprocess import run

from tasks.faasm import get_faasm_upload_host_port
from tasks.util import (
    COVID_DIR,
    WASM_BUILD_DIR,
    FAASM_USER,
    FAASM_FUNC,
    FAASM_WASM_DIR,
)

CMAKE_TOOLCHAIN_FILE = "/usr/local/faasm/toolchain/tools/WasiToolchain.cmake"


@task(default=True)
def build(ctx, clean=False, verbose=False):
    """
    Builds the function for Faasm
    """
    if clean and exists(WASM_BUILD_DIR):
        rmtree(WASM_BUILD_DIR)

    makedirs(WASM_BUILD_DIR, exist_ok=True)

    cmake_cmd = [
        "cmake",
        "-GNinja",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_TOOLCHAIN_FILE={}".format(CMAKE_TOOLCHAIN_FILE),
        "-DFAASM_COVID=ON",
        COVID_DIR,
    ]
    cmake_cmd_str = " ".join(cmake_cmd)

    run(cmake_cmd_str, shell=True, check=True, cwd=WASM_BUILD_DIR)

    run(
        "cmake --build . --target all {}".format(
            "--verbose" if verbose else ""
        ),
        shell=True,
        check=True,
        cwd=WASM_BUILD_DIR,
    )

    # Also copy into place locally
    wasm_file = join(WASM_BUILD_DIR, "src", "CovidSim")
    if exists(FAASM_WASM_DIR):
        target_dir = join(FAASM_WASM_DIR, "cov", "sim")
        makedirs(target_dir, exist_ok=True)
        target_file = join(target_dir, "function.wasm")
        run("cp {} {}".format(wasm_file, target_file), shell=True, check=True)
        print("Copied wasm into place at {}".format(target_file))


@task
def upload(ctx):
    host, port = get_faasm_upload_host_port()
    wasm_file = join(WASM_BUILD_DIR, "src", "CovidSim")

    url = "http://{}:{}/f/{}/{}".format(host, port, FAASM_USER, FAASM_FUNC)
    response = requests.put(url, data=open(wasm_file, "rb"))

    print("Response {}: {}".format(response.status_code, response.text))
