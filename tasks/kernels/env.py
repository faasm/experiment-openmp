from os.path import join
from tasks.util import PROJ_ROOT, RESULTS_DIR

KERNELS_NATIVE_DIR = join(PROJ_ROOT, "third-party", "kernels")
KERNELS_WASM_DIR = join(PROJ_ROOT, "third-party", "kernels-wasm")

KERNELS_FAASM_USER = "omp"

SUPPORTED_KERNELS = [
    ("OPENMP/DGEMM", "dgemm"),
    ("OPENMP/Nstream", "nstream"),
    ("OPENMP/PIC", "pic"),
    ("OPENMP/Random", "random"),
    ("OPENMP/Reduce", "reduce"),
    ("OPENMP/Sparse", "sparse"),
    ("OPENMP/Stencil", "stencil"),
    ("OPENMP/Synch_global", "global"),
    ("OPENMP/Synch_p2p", "p2p"),
    ("OPENMP/Transpose", "transpose"),
]

# Issues:
#
# - Random errors when running natively
# - PIC requires new init
# - Transpose requires new init
# - Global doesn't work across hosts
# - Reduce doesn't scale natively
KERNELS_NON_WASM = ["pic", "global", "random", "reduce", "transpose"]

# See PRK CI scripts for example arguments:
# https://github.com/ParRes/Kernels/blob/default/ci/build-run-prk.sh
KERNELS_CMDLINE = {
    # dgemm: iterations, matrix order
    "dgemm": [10, 1400, 32],
    # global: iterations, scramble string length
    "global": [10, 100000],
    # nstream: iterations, vector length, offset
    "nstream": [10, 100000000, 32],
    # p2p: iterations, 1st array dimension, 2nd array dimension
    "p2p": [10, 20000, 20000],
    # pic: simulation steps, grid size, n particles, k, m
    "pic": [10, 1000, 5000000, 1, 0, "LINEAR", 1.0, 3.0],
    # reduce: iterations, vector length
    "reduce": [10, 10000000],
    # sparse: iterations, 2log grid size, radius
    "sparse": [10, 10, 12],
    # stencil: iterations, array dimension
    "stencil": [10, 10000],
    # transpose: iterations, matrix order, tile size
    "transpose": [10, 8000, 32],
}

# The following kernels scale nicely with increasing threads
SCALING_KERNELS = ["dgemm"]

# Kernel stats, put avg time first
KERNELS_STATS = {
    "dgemm": ("Avg time (s)", "Rate (MFlops/s)"),
    "global": ("time (s)", "Rate (synch/s)"),
    "nstream": ("Avg time (s)", "Rate (MB/s)"),
    "p2p": ("Avg time (s)", "Rate (MFlops/s)"),
    "pic": ("Rate (Mparticles_moved/s)",),
    "reduce": ("Avg time (s)", "Rate (MFlops/s)"),
    "sparse": ("Avg time (s)", "Rate (MFlops/s)"),
    "stencil": ("Avg time (s)", "Rate (MFlops/s)"),
    "transpose": ("Avg time (s)", "Rate (MB/s)"),
}

KERNELS_NATIVE_EXECUTABLES = {
    "dgemm": join(KERNELS_NATIVE_DIR, "OPENMP", "DGEMM", "dgemm"),
    "global": join(KERNELS_NATIVE_DIR, "OPENMP", "Synch_global", "global"),
    "nstream": join(KERNELS_NATIVE_DIR, "OPENMP", "Nstream", "nstream"),
    "p2p": join(KERNELS_NATIVE_DIR, "OPENMP", "Synch_p2p", "p2p"),
    "pic": join(KERNELS_NATIVE_DIR, "OPENMP", "PIC", "pic"),
    "reduce": join(KERNELS_NATIVE_DIR, "OPENMP", "Reduce", "reduce"),
    "sparse": join(KERNELS_NATIVE_DIR, "OPENMP", "Sparse", "sparse"),
    "stencil": join(KERNELS_NATIVE_DIR, "OPENMP", "Stencil", "stencil"),
    "transpose": join(KERNELS_NATIVE_DIR, "OPENMP", "Transpose", "transpose"),
}

WASM_RESULT_FILE = join(RESULTS_DIR, "kernels_wasm.csv")
NATIVE_RESULT_FILE = join(RESULTS_DIR, "kernels_native.csv")
