from copy import copy
from os.path import join
from subprocess import run
from os import environ

FAASM_LOCAL_DIR = environ.get("FAASM_LOCAL_DIR", "/usr/local/faasm")
WASM_SYSROOT = join(FAASM_LOCAL_DIR, "llvm-sysroot")
WASM_TOOLCHAIN_ROOT = "/usr/local/faasm/toolchain"
WASM_TOOLCHAIN_TOOLS = join(WASM_TOOLCHAIN_ROOT, "tools")
WASM_TOOLCHAIN_BIN = join(WASM_TOOLCHAIN_ROOT, "bin")

# Toolchain files
CMAKE_TOOLCHAIN_FILE = join(WASM_TOOLCHAIN_TOOLS, "WasiToolchain.cmake")

# Executables
WASM_CC = join(WASM_TOOLCHAIN_BIN, "clang")
WASM_CXX = join(WASM_TOOLCHAIN_BIN, "clang++")
WASM_CPP = join(WASM_TOOLCHAIN_BIN, "clang-cpp")
WASM_AR = join(WASM_TOOLCHAIN_BIN, "llvm-ar")
WASM_AS = join(WASM_TOOLCHAIN_BIN, "llvm-as")
WASM_NM = join(WASM_TOOLCHAIN_BIN, "llvm-nm")
WASM_RANLIB = join(WASM_TOOLCHAIN_BIN, "llvm-ranlib")

# Use top-level clang as the linker rather than invoking wasm-ld directly
WASM_LD = WASM_CC
WASM_LDXX = WASM_CXX

# Host triple
WASM_BUILD = "wasm32"
WASM_HOST = "wasm32-unknown-wasi"
WASM_HOST_UNKNOWN = "wasm32-unknown-unknown"

# CFLAGS
WASM_CFLAGS = [
    "-m32",
    "-DCONFIG_32",
    "-DANSI",
    "-O3",
    "--sysroot={}".format(WASM_SYSROOT),
    "-D__faasm",
]

WASM_CXXFLAGS = WASM_CFLAGS

WASM_LDFLAGS = [
    "-static",
    "-Xlinker --no-gc-sections",
    "-Xlinker --stack-first",
    "-Xlinker --no-check-features",
]

CONFIG_ENV = {
    "CC": WASM_CC,
    "PTHREADCC": WASM_CC,
    "CXX": WASM_CXX,
    "CPP": WASM_CPP,
    "AR": WASM_AR,
    "AS": WASM_AS,
    "LD": WASM_LD,
    "RANLIB": WASM_RANLIB,
    "CFLAGS": " ".join(WASM_CFLAGS),
    "CPPFLAGS": " ".join(WASM_CFLAGS),
    "CXXFLAGS": " ".join(WASM_CXXFLAGS),
    "LIBS": "-lfaasmp -lfaasm",
}
