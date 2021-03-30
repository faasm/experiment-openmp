from invoke import task
from shutil import rmtree, copyfile
from os.path import exists, join
from os import makedirs
from tasks.util import COVID_DIR, WASM_BUILD_DIR
from subprocess import run

CMAKE_TOOLCHAIN_FILE = "/usr/local/faasm/toolchain/tools/WasiToolchain.cmake"
FAASM_USER = "cov"
FAASM_FUNC = "sim"


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

    # Do the local upload
    upload(ctx, local=True)


@task
def upload(ctx, local=False):
    wasm_file = join(WASM_BUILD_DIR, "src", "CovidSim")

    if not local:
        print("Remote upload not implemented yet")
        exit(1)

    dest_dir = "/usr/local/faasm/wasm/{}/{}".format(FAASM_USER, FAASM_FUNC)
    makedirs(dest_dir, exist_ok=True)

    dest_file = join(dest_dir, "function.wasm")
    copyfile(wasm_file, dest_file)
