from glob import glob
from invoke import task
from os import makedirs, listdir
from os.path import join, exists

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from tasks.kernels.env import WASM_RESULT_FILE, NATIVE_RESULT_FILE
from tasks.util import PLOTS_FORMAT, PLOTS_ROOT, PROJ_ROOT, RESULTS_DIR

PLOTS_DIR = join(PLOTS_ROOT, "lulesh")
RUNTIME_PLOT_FILE = join(PLOTS_ROOT, "kernels_runtime.{}".format(PLOTS_FORMAT))


def _read_results(csv_file):
    results = pd.read_csv(csv_file)

    grouped = results.groupby(["Kernel", "Threads"])
    times = grouped.mean()
    errs = grouped.std()

    return grouped, times, errs


@task(default=True)
def plot(ctx):
    """
    Plot Kernels figure
    """
    makedirs(PLOTS_DIR, exist_ok=True)

    # Load results
    native_grouped, native_times, native_errs = _read_results(
        NATIVE_RESULT_FILE
    )

    fig, ax = plt.subplots()

    native_times.plot.line(
        y="Actual",
        yerr=native_errs,
        ecolor="gray",
        elinewidth=0.8,
        capsize=1.0,
        ax=ax,
        label="Native",
    )

    ax.set_ylim(0)
    ax.set_xlim(0, 20)

    fig.tight_layout()
    plt.gca().set_aspect(0.1)
    plt.savefig(RUNTIME_PLOT_FILE, format=PLOTS_FORMAT, bbox_inches="tight")
