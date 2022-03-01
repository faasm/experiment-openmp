from os.path import join

from tasks.util import (
    PROJ_ROOT,
)

LULESH_NATIVE_BUILD_DIR = join(PROJ_ROOT, "build", "lulesh", "native")
LULESH_WASM_BUILD_DIR = join(PROJ_ROOT, "build", "lulesh", "wasm")
LULESH_DIR = join(PROJ_ROOT, "third-party", "lulesh")

NATIVE_BINARY = join(LULESH_NATIVE_BUILD_DIR, "lulesh2.0")
WASM_BINARY = join(LULESH_WASM_BUILD_DIR, "lulesh2.0")
WASM_USER = "lulesh"
WASM_FUNC = "func"
