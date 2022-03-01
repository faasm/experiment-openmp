from os.path import join
from tasks.util import PROJ_ROOT

KERNELS_NATIVE_DIR = join(PROJ_ROOT, "third-party", "kernels")
KERNELS_WASM_DIR = join(PROJ_ROOT, "third-party", "kernels-wasm")

KERNELS_FAASM_USER = "omp"
