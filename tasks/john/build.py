from subprocess import run
from invoke import task
import requests
import os
from copy import copy
from os import makedirs
from os.path import exists, join
from shutil import rmtree
import multiprocessing


from tasks.faasm import get_faasm_upload_host_port

from tasks.util import (
    CMAKE_TOOLCHAIN_FILE,
    FAASM_WASM_DIR,
)

from tasks.john.env import (
    JOHN_NATIVE_BUILD_DIR,
    JOHN_DIR,
    JOHN_SRC_DIR,
    JOHN_WASM_BUILD_DIR,
    WASM_BINARY,
    WASM_FUNC,
    WASM_USER,
)

from tasks.compile import (
    CONFIG_CMD_FLAGS,
    WASM_SYSROOT,
    WASM_CC,
    WASM_CXX,
    WASM_AR,
    WASM_NM,
    WASM_RANLIB,
    WASM_CFLAGS,
    WASM_LDFLAGS,
)

JOHN_ENV = {
    "OMP_NUM_THREADS": "2",
    "PLUGS": "none",
    "UNIT_TESTS": "no",
    "BUILD_OPTS": "--enable-werror CPPFLAGS=-DDYNAMIC_DISABLED",
}


@task
def native(ctx, clean=False):
    """
    Compile John natively
    """
    if clean:
        run("make clean", check=True, shell=True, cwd=JOHN_SRC_DIR)

    env = copy(os.environ)
    env = env.update(JOHN_ENV)

    configure_cmd = [
        "./configure",
        "--enable-werror CPPFLAGS=-DDYNAMIC_DISABLED",
    ]

    run(
        " ".join(configure_cmd),
        shell=True,
        check=True,
        cwd=JOHN_SRC_DIR,
    )

    n_cpus = multiprocessing.cpu_count()
    make_cmd = ["make -j {}".format(n_cpus - 1)]
    run(
        " ".join(make_cmd),
        shell=True,
        check=True,
        cwd=JOHN_SRC_DIR,
    )


@task
def wasm(ctx, clean=False):
    """
    Compile John to wasm
    """
    if clean:
        run("make clean", check=True, shell=True, cwd=JOHN_SRC_DIR)

    env = copy(os.environ)
    env = env.update(JOHN_ENV)

    env.update(
        {
            "CFLAGS": " ".join(WASM_CFLAGS),
            "CXXFLAGS": " ".join(WASM_CFLAGS),
            "LDFLAGS": " ".join(WASM_LDFLAGS),
            "NM": WASM_NM,
            "AR": WASM_AR,
            "RANLIB": WASM_RANLIB,
            "CC": WASM_CC,
            "CXX": WASM_CXX,
        }
    )

    configure_cmd = [
        "./configure",
        "--prefix={}".format(WASM_SYSROOT),
        "--enable-werror CPPFLAGS=-DDYNAMIC_DISABLED",
    ]
    configure_cmd.extend(CONFIG_CMD_FLAGS)
    configure_cmd = " ".join(configure_cmd)
    print(configure_cmd)

    run(
        " ".join(configure_cmd),
        shell=True,
        check=True,
        cwd=JOHN_SRC_DIR,
    )

    n_cpus = multiprocessing.cpu_count()
    make_cmd = ["make -j {}".format(n_cpus - 1)]
    run(
        " ".join(make_cmd),
        shell=True,
        check=True,
        cwd=JOHN_SRC_DIR,
    )


@task
def upload(ctx):
    host, port = get_faasm_upload_host_port()

    url = "http://{}:{}/f/{}/{}".format(host, port, WASM_USER, WASM_FUNC)
    response = requests.put(url, data=open(WASM_BINARY, "rb"))

    print("Response {}: {}".format(response.status_code, response.text))
