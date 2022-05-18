from os.path import dirname, realpath, expanduser, join

HOME_DIR = expanduser("~")
PROJ_ROOT = dirname(dirname(realpath(__file__)))

FAASM_LOCAL_DIR = "/usr/local/faasm"
WASM_TOOLCHAIN_ROOT = "/usr/local/faasm/toolchain"
WASM_TOOLCHAIN_TOOLS = join(WASM_TOOLCHAIN_ROOT, "tools")
WASM_SYSROOT = "/usr/local/faasm/llvm-sysroot"

# Toolchain files
CMAKE_TOOLCHAIN_FILE = join(WASM_TOOLCHAIN_TOOLS, "WasiToolchain.cmake")

COVID_DIR = join(PROJ_ROOT, "third-party", "covid-sim")
DATA_DIR = join(COVID_DIR, "data")
NATIVE_BUILD_DIR = join(PROJ_ROOT, "build", "native")
WASM_BUILD_DIR = join(PROJ_ROOT, "build", "wasm")

PLOTS_ROOT = join(PROJ_ROOT, "plots")
PLOTS_FORMAT = "pdf"

PLOTS_MAX_THREADS = 44

FAASM_LOCAL_DIR = "/usr/local/faasm"
FAASM_WASM_DIR = join(FAASM_LOCAL_DIR, "wasm")

IS_DOCKER = HOME_DIR.startswith("/root")

RESULTS_DIR = join(PROJ_ROOT, "results")


def get_version():
    ver_file = join(PROJ_ROOT, "VERSION")

    with open(ver_file, "r") as fh:
        version = fh.read()
        version = version.strip()

    return version
