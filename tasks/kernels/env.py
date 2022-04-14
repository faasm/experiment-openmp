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
    ("OPENMP/Sparse", "sparse"),
    ("OPENMP/Stencil", "stencil"),
    ("OPENMP/Synch_global", "global"),
    ("OPENMP/Synch_p2p", "p2p"),
]

KERNELS_CMDLINE = {
    # dgemm: iterations, matrix order
    "dgemm": [400, 400],
    # global: iterations, scramble string length
    "global": [5000, 500000],
    # nstream: iterations, vector length, offset
    "nstream": [20000, 400000, 0],
    # p2p: iterations, 1st array dimension, 2nd array dimension
    "p2p": [750, 10000, 1000],
    # random: log2 table size, update ratio, vector length
    # Update ratio must be divisible by vector length
    # "random": [16, 5000, 1000], # Seems to error even running native
    # reduce: iterations, vector length
    "reduce": [20000, 40000],
    # sparse: iterations, 2log grid size, radius
    "sparse": [400, 10, 4],
    # stencil: iterations, array dimension
    "stencil": [200, 5000],
}

# Kernel stats, put avg time first
KERNELS_STATS = {
    "dgemm": ("Avg time (s)", "Rate (MFlops/s)"),
    "global": ("time (s)", "Rate (synch/s)"),
    "nstream": ("Avg time (s)", "Rate (MB/s)"),
    "p2p": ("Avg time (s)", "Rate (MFlops/s)"),
    "reduce": ("Avg time (s)", "Rate (MFlops/s)"),
    "sparse": ("Avg time (s)", "Rate (MFlops/s)"),
    "stencil": ("Avg time (s)", "Rate (MFlops/s)"),
}

KERNELS_NATIVE_EXECUTABLES = {
    "dgemm": join(KERNELS_NATIVE_DIR, "OPENMP", "DGEMM", "dgemm"),
    "global": join(KERNELS_NATIVE_DIR, "OPENMP", "Synch_global", "global"),
    "nstream": join(KERNELS_NATIVE_DIR, "OPENMP", "Nstream", "nstream"),
    "p2p": join(KERNELS_NATIVE_DIR, "OPENMP", "Synch_p2p", "p2p"),
    "random": join(KERNELS_NATIVE_DIR, "OPENMP", "Random", "random"),
    "reduce": join(KERNELS_NATIVE_DIR, "OPENMP", "Reduce", "reduce"),
    "sparse": join(KERNELS_NATIVE_DIR, "OPENMP", "Sparse", "sparse"),
    "stencil": join(KERNELS_NATIVE_DIR, "OPENMP", "Stencil", "stencil"),
}

WASM_RESULT_FILE = join(RESULTS_DIR, "kernels_wasm.csv")
NATIVE_RESULT_FILE = join(RESULTS_DIR, "kernels_native.csv")
