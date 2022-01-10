from subprocess import run
from invoke import task
from os import makedirs, listdir
from os.path import exists, join
from shutil import rmtree
from subprocess import run

from os.path import join

from invoke import task

from tasks.util import (
    PROJ_ROOT,
    CMAKE_TOOLCHAIN_FILE,
    FAASM_WASM_DIR
)

LULESH_NATIVE_BUILD_DIR = join(PROJ_ROOT, "build", "lulesh", "native")
LULESH_WASM_BUILD_DIR = join(PROJ_ROOT, "build", "lulesh", "wasm")
LULESH_DIR = join(PROJ_ROOT, "third-party", "lulesh")


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
    wasm_file = join(LULESH_WASM_BUILD_DIR, "lulesh2.0")
    if exists(FAASM_WASM_DIR):
        target_dir = join(FAASM_WASM_DIR, "lulesh", "func")
        makedirs(target_dir, exist_ok=True)
        target_file = join(target_dir, "function.wasm")
        run("cp {} {}".format(wasm_file, target_file), shell=True, check=True)
        print("Copied wasm into place at {}".format(target_file))
