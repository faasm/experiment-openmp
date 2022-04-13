from invoke import task
from os.path import join, exists
from os import makedirs
from subprocess import run
import shutil
import requests

from tasks.faasm import get_faasm_upload_host_port
from tasks.util import FAASM_LOCAL_DIR
from tasks.kernels.env import (
    KERNELS_NATIVE_DIR,
    KERNELS_WASM_DIR,
    KERNELS_FAASM_USER,
    SUPPORTED_KERNELS,
)


@task
def native(ctx, clean=False):
    """
    Build native kernels
    """
    print("Running kernels native build in {}".format(KERNELS_NATIVE_DIR))
    _do_build(KERNELS_NATIVE_DIR, clean, False)


@task
def wasm(ctx, clean=False):
    """
    Build kernels to wasm
    """
    print("Running kernels wasm build in {}".format(KERNELS_WASM_DIR))
    _do_build(KERNELS_WASM_DIR, clean, True)


def _do_build(src_dir, clean, is_wasm):
    if clean:
        print("Cleaning {}".format(src_dir))
        run("make clean", shell=True, cwd=src_dir)

    for relative_dir, target in SUPPORTED_KERNELS:
        work_dir = join(src_dir, relative_dir)
        print("Making {} in {}".format(target, work_dir))
        run("make {}".format(target), shell=True, cwd=work_dir)

        # Copy wasm file into place locally
        if is_wasm:
            local_dir = join(
                FAASM_LOCAL_DIR, "wasm", KERNELS_FAASM_USER, target
            )

            if not exists(local_dir):
                print("Creating {}".format(local_dir))
                makedirs(local_dir)

            local_file = join(local_dir, "function.wasm")
            wasm_file = join(
                KERNELS_WASM_DIR, "wasm", "{}.wasm".format(target)
            )

            print("Copying {} to {}".format(wasm_file, local_file))
            shutil.copy(wasm_file, local_file)


@task
def upload(ctx):
    """
    Upload kernels function to Faasm
    """
    host, port = get_faasm_upload_host_port()

    for rel_dir, target in SUPPORTED_KERNELS:
        wasm_file = join(KERNELS_WASM_DIR, "wasm", "{}.wasm".format(target))

        url = "http://{}:{}/f/{}/{}".format(
            host, port, KERNELS_FAASM_USER, target
        )
        print("Putting function to {}".format(url))
        response = requests.put(url, data=open(wasm_file, "rb"))
        print("Response {}: {}".format(response.status_code, response.text))
