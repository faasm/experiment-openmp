from invoke import task
from os.path import join
from subprocess import run
import requests

from tasks.faasm import get_faasm_upload_host_port
from tasks.kernels.env import (
    KERNELS_NATIVE_DIR,
    KERNELS_WASM_DIR,
    KERNELS_FAASM_USER,
)

SUPPORTED_KERNELS = [
    ("OPENMP/DGEMM", "dgemm"),
    ("OPENMP/Nstream", "nstream"),
    ("OPENMP/Reduce", "reduce"),
    ("OPENMP/Stencil", "stencil"),
    ("OPENMP/Random", "random"),
    ("OPENMP/Sparse", "sparse"),
    ("OPENMP/Synch_global", "global"),
    ("OPENMP/Synch_p2p", "p2p"),
    ("OPENMP/Branch", "branch"),
]


@task
def native(ctx, clean=False):
    """
    Build native kernels
    """
    _do_build(KERNELS_NATIVE_DIR, clean)


@task
def wasm(ctx, clean=False):
    """
    Build kernels to wasm
    """
    _do_build(KERNELS_WASM_DIR, clean)


def _do_build(src_dir, clean):
    if clean:
        run("make clean", shell=True, cwd=src_dir)

    for src_dir, target in SUPPORTED_KERNELS:
        d = join(KERNELS_WASM_DIR, src_dir)
        run("make {}".format(target), shell=True, cwd=d)


@task
def upload(ctx):
    """
    Upload kernels function to Faasm
    """
    host, port = get_faasm_upload_host_port()

    for src_dir, target in SUPPORTED_KERNELS:
        wasm_file = join(KERNELS_WASM_DIR, "wasm", "{}.wasm".format(target))

        url = "http://{}:{}/f/{}/{}".format(
            host, port, KERNELS_FAASM_USER, target
        )
        print("Putting function to {}".format(url))
        response = requests.put(url, data=open(wasm_file, "rb"))
        print("Response {}: {}".format(response.status_code, response.text))
