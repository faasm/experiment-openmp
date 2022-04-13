from os.path import join
from tasks.util import PROJ_ROOT, RESULTS_DIR

KERNELS_NATIVE_DIR = join(PROJ_ROOT, "third-party", "kernels")
KERNELS_WASM_DIR = join(PROJ_ROOT, "third-party", "kernels-wasm")

KERNELS_FAASM_USER = "omp"

SUPPORTED_KERNELS = [
    ("OPENMP/Branch", "branch"),
    ("OPENMP/DGEMM", "dgemm"),
    ("OPENMP/Nstream", "nstream"),
    ("OPENMP/Random", "random"),
    ("OPENMP/Reduce", "reduce"),
    ("OPENMP/Stencil", "stencil"),
    ("OPENMP/Sparse", "sparse"),
    ("OPENMP/Synch_global", "global"),
    ("OPENMP/Synch_p2p", "p2p"),
]

KERNELS_CMDLINE = {
    "dgemm": [400, 400],
    # dgemm: iterations, matrix order
    "nstream": [20000, 200000, 0],
    # nstream: iterations, vector length, offset
    "reduce": [40000, 20000],
    # reduce: iterations, vector length
    "stencil": [200, 5000],
    # stencil: iterations, array dimension
    "global": [5000, 250000],
    # global: iterations, scramble string length
    "p2p": [750, 10000, 1000],
    # p2p: iterations, 1st array dimension, 2nd array dimension
}

KERNELS_STATS = {
    "dgemm": ("Avg time (s)", "Rate (MFlops/s)"),
    "nstream": ("Avg time (s)", "Rate (MB/s)"),
    "reduce": ("Avg time (s)", "Rate (MFlops/s)"),
    "stencil": ("Avg time (s)", "Rate (MFlops/s)"),
    "global": ("time (s)", "Rate (synch/s)"),
    "p2p": ("Avg time (s)", "Rate (MFlops/s)"),
}

KERNELS_NATIVE_EXECUTABLES = {
    "dgemm": join(KERNELS_NATIVE_DIR, "OPENMP", "DGEMM", "dgemm"),
    "nstream": join(KERNELS_NATIVE_DIR, "OPENMP", "Nstream", "nstream"),
    "reduce": join(KERNELS_NATIVE_DIR, "OPENMP", "Reduce", "reduce"),
    "stencil": join(KERNELS_NATIVE_DIR, "OPENMP", "Stencil", "stencil"),
    "global": join(KERNELS_NATIVE_DIR, "OPENMP", "Synch_global", "global"),
    "p2p": join(KERNELS_NATIVE_DIR, "OPENMP", "Synch_p2p", "p2p"),
}

WASM_RESULT_FILE = join(RESULTS_DIR, "kernels_wasm.csv")
NATIVE_RESULT_FILE = join(RESULTS_DIR, "kernels_native.csv")
