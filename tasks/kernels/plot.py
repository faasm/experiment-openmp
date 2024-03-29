from invoke import task
from os import makedirs
from os.path import join, exists

import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from tasks.kernels.env import (
    WASM_RESULT_FILE,
    NATIVE_RESULT_FILE,
    KERNELS_CMDLINE,
)
from tasks.util import (
    MPL_STYLE_FILE,
    PLOTS_FORMAT,
    PLOTS_ROOT,
    PLOTS_MAX_THREADS,
)

PLOT_KERNELS = list(KERNELS_CMDLINE.keys())

SINGLE_HOST_LINE = 15

RUNTIME_PLOT_FILE = join(PLOTS_ROOT, "kernels_runtime.{}".format(PLOTS_FORMAT))


def _read_results(csv_file):
    if not exists(csv_file):
        return list(), dict()

    data = pd.read_csv(csv_file)

    grouped = data.groupby(["Kernel"])

    results = dict()

    for name, group in grouped:
        by_thread = group.groupby(["Threads"])

        threads = [int(t) for t in by_thread.groups.keys()]
        times = by_thread.mean()["Actual"].values
        errs = by_thread.std()["Actual"].values
        errs = [np.nan_to_num(e) for e in errs]

        results[name] = {
            "threads": threads,
            "times": times,
            "errs": errs,
        }

    kernels = results.keys()

    return kernels, results


@task(default=True)
def plot(ctx, headless=False, kernel=None):
    """
    Plot Kernels figure
    """
    # Use our matplotlib style file
    plt.style.use(MPL_STYLE_FILE)

    if kernel:
        kernels = [kernel]
        rows = 1
        cols = 1
    else:
        kernels = PLOT_KERNELS
        rows = 2
        cols = -(-len(kernels) // 2)

    # Load results
    native_kernels, native_results = _read_results(NATIVE_RESULT_FILE)

    wasm_kernels, wasm_results = _read_results(WASM_RESULT_FILE)

    fig = plt.figure(figsize=(5, 2))

    for i, kernel in enumerate(kernels):
        native_result = native_results.get(kernel, dict())
        wasm_result = wasm_results.get(kernel, dict())

        subax = plt.subplot(rows, cols, i + 1)

        if len(kernels) > 1:
            plt.title(kernel)

        max_native_time = 0
        max_wasm_time = 0
        max_natve_threads = 0
        max_wasm_threads = 0

        if wasm_result:
            plt.errorbar(
                x=wasm_result["threads"],
                y=wasm_result["times"],
                yerr=wasm_result["errs"],
                label="Granny",
            )

            max_wasm_threads = np.max(wasm_result["threads"])
            max_wasm_time = np.max(wasm_result["times"])

        if native_result:
            plt.errorbar(
                x=native_result["threads"],
                y=native_result["times"],
                yerr=native_result["errs"],
                label="OpenMP",
            )

            max_native_threads = np.max(native_result["threads"])
            max_native_time = np.max(native_result["times"])

        # Add single host marker lines
        max_threads = np.max([max_native_threads, max_wasm_threads])
        single_host_lines = [
            SINGLE_HOST_LINE,
            (2 * SINGLE_HOST_LINE) + 1,
            (3 * SINGLE_HOST_LINE) + 2,
        ]
        single_host_lines = [s for s in single_host_lines if s <= max_threads]

        for x in single_host_lines:
            plt.axvline(x=x, color="tab:red", linestyle="--")

        max_y = math.ceil(np.max([max_native_time, max_wasm_time]))

        subax.set_ylabel("Time (s)")
        subax.set_xlabel("# threads")

        plt.legend()
        plt.gca().set_ylim(0, max_y)
        plt.gca().set_xlim(0, PLOTS_MAX_THREADS)

    fig.tight_layout()

    if headless:
        print("Saving plot to {}".format(RUNTIME_PLOT_FILE))
        plt.savefig(
            RUNTIME_PLOT_FILE, format=PLOTS_FORMAT, bbox_inches="tight"
        )
    else:
        plt.show()
