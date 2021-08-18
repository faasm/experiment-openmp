from invoke import task
import requests
from shutil import rmtree
from os.path import exists, join
from os import makedirs
from tasks.util import COVID_DIR, WASM_BUILD_DIR, FAASM_USER, FAASM_FUNC
from subprocess import run

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


@task
def upload(ctx, host="localhost", port=8002):
    wasm_file = join(WASM_BUILD_DIR, "src", "CovidSim")

    url = "http://{}:{}/f/{}/{}".format(host, port, FAASM_USER, FAASM_FUNC)
    response = requests.put(url, data=open(wasm_file, "rb"))

    print("Response {}: {}".format(response.status_code, response.text))
