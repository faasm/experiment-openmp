from os.path import join

from tasks.util import (
    PROJ_ROOT,
)

JOHN_NATIVE_BUILD_DIR = join(PROJ_ROOT, "build", "john", "native")
JOHN_WASM_BUILD_DIR = join(PROJ_ROOT, "build", "john", "wasm")
JOHN_DIR = join(PROJ_ROOT, "third-party", "john")
JOHN_SRC_DIR = join(JOHN_DIR, "src")

NATIVE_BINARY = join(JOHN_NATIVE_BUILD_DIR, "john2.0")
WASM_BINARY = join(JOHN_WASM_BUILD_DIR, "john2.0")
WASM_USER = "john"
WASM_FUNC = "func"
