from invoke import task
from os import makedirs
from os.path import join, exists

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from tasks.kernels.env import (
    WASM_RESULT_FILE,
    NATIVE_RESULT_FILE,
    KERNELS_CMDLINE,
)
from tasks.util import PLOTS_FORMAT, PLOTS_ROOT, PROJ_ROOT, RESULTS_DIR

PLOT_KERNELS = list(KERNELS_CMDLINE.keys())

PLOTS_DIR = join(PLOTS_ROOT, "lulesh")
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
def plot(ctx, headless=False):
    """
    Plot Kernels figure
    """
    makedirs(PLOTS_DIR, exist_ok=True)

    # Load results
    native_kernels, native_results = _read_results(NATIVE_RESULT_FILE)

    wasm_kernels, wasm_results = _read_results(WASM_RESULT_FILE)

    fig, ax = plt.subplots()
    rows = 2
    cols = -(-len(PLOT_KERNELS) // 2)

    for i, kernel in enumerate(PLOT_KERNELS):
        native_result = native_results.get(kernel, dict())
        wasm_result = wasm_results.get(kernel, dict())

        plt.subplot(rows, cols, i + 1)

        plt.title(kernel)

        if native_result:
            plt.errorbar(
                x=native_result["threads"],
                y=native_result["times"],
                yerr=native_result["errs"],
                color="tab:blue",
                label="Native",
            )

        if wasm_result:
            plt.errorbar(
                x=wasm_result["threads"],
                y=wasm_result["times"],
                yerr=wasm_result["errs"],
                color="tab:orange",
                label="Faasm",
            )

        plt.legend()
        plt.gca().set_ylim(0)

    fig.tight_layout()

    if headless:
        plt.savefig(
            RUNTIME_PLOT_FILE, format=PLOTS_FORMAT, bbox_inches="tight"
        )
    else:
        plt.show()
