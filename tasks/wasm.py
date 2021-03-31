from invoke import task
import requests
from shutil import rmtree, copyfile
from os.path import exists, join
from os import makedirs
from tasks.util import COVID_DIR, WASM_BUILD_DIR, FAASM_USER, FAASM_FUNC
from subprocess import run

CMAKE_TOOLCHAIN_FILE = "/usr/local/faasm/toolchain/tools/WasiToolchain.cmake"


@task(default=True)
def build(ctx, clean=False):
    """
    Builds the function for Faasm
    """
    if clean and exists(WASM_BUILD_DIR):
        rmtree(WASM_BUILD_DIR)

    makedirs(WASM_BUILD_DIR, exist_ok=True)

    cmake_cmd = [
        "VERBOSE=1",
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
        "cmake --build . --target all",
        shell=True,
        check=True,
        cwd=WASM_BUILD_DIR,
    )

    # Do the local upload
    upload(ctx, local=True)


@task
def upload(ctx, host="faasm", port=8002, local=False):
    wasm_file = join(WASM_BUILD_DIR, "src", "CovidSim")

    if local:
        dest_dir = "/usr/local/faasm/wasm/{}/{}".format(FAASM_USER, FAASM_FUNC)
        makedirs(dest_dir, exist_ok=True)

        dest_file = join(dest_dir, "function.wasm")
        copyfile(wasm_file, dest_file)
    else:
        url = "http://{}:{}/f/{}/{}".format(host, port, FAASM_USER, FAASM_FUNC)
        response = requests.put(url, data=open(wasm_file, "rb"))

        print("Response {}: {}".format(response.status_code, response.text))
