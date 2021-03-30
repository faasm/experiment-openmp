from invoke import task
from shutil import rmtree
from os.path import exists
from os import makedirs
from tasks.util import COVID_DIR, WASM_BUILD_DIR
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
