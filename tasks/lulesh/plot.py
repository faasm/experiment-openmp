from glob import glob
from invoke import task
from os import makedirs, listdir
from os.path import join, exists

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from tasks.util import (
    MPL_STYLE_FILE,
    PLOTS_FORMAT,
    PLOTS_ROOT,
    PROJ_ROOT,
    PLOTS_MAX_THREADS,
)

RESULTS_DIR = join(PROJ_ROOT, "results")
RUNTIME_PLOT_FILE = join(PLOTS_ROOT, "lulesh_runtime.{}".format(PLOTS_FORMAT))
SIMPLE_PLOT_FILE = join(PLOTS_ROOT, "lulesh.png")

WASM_RESULT_FILE = join(RESULTS_DIR, "lulesh_wasm.csv")
NATIVE_RESULT_FILE = join(RESULTS_DIR, "lulesh_native.csv")

SINGLE_HOST_LINE = 15


def _read_results(result_file):

    data = pd.read_csv(result_file)
    by_thread = data.groupby(["Threads"])

    threads = [int(t) for t in by_thread.groups.keys()]
    times = by_thread.mean()["Actual"].values
    errs = by_thread.std()["Actual"].values
    errs = [np.nan_to_num(e) for e in errs]

    results = {
        "threads": threads,
        "times": times,
        "errs": errs,
    }

    return results


@task(default=True)
def plot(ctx, headless=False):
    """
    Plot LULESH figure
    """
    # Use our matplotlib style file
    plt.style.use(MPL_STYLE_FILE)

    makedirs(PLOTS_ROOT, exist_ok=True)

    # Load results
    native_result = _read_results(NATIVE_RESULT_FILE)
    wasm_result = _read_results(WASM_RESULT_FILE)

    fig = plt.figure(figsize=(5, 2))

    # Plot Granny results
    plt.errorbar(
        x=wasm_result["threads"],
        y=wasm_result["times"],
        yerr=wasm_result["errs"],
        label="Granny",
    )

    # Plot results - native
    plt.errorbar(
        x=native_result["threads"],
        y=native_result["times"],
        yerr=native_result["errs"],
        label="OpenMP",
    )

    plt.axvline(x=SINGLE_HOST_LINE, color="tab:red", linestyle="--")
    plt.axvline(x=2 * SINGLE_HOST_LINE, color="tab:red", linestyle="--")

    # Aesthetics
    ax = plt.gca()
    ax.set_ylabel("Time (s)")
    ax.set_xlabel("# threads")
    ax.set_ylim(0)
    ax.set_xlim(0, PLOTS_MAX_THREADS)

    plt.legend()

    fig.tight_layout()

    if headless:
        plt.gca().set_aspect(0.1)
        print("Saving plot to {}".format(RUNTIME_PLOT_FILE))
        plt.savefig(
            RUNTIME_PLOT_FILE, format=PLOTS_FORMAT, bbox_inches="tight"
        )
    else:
        plt.show()


@task
def simple(ctx, headless=False):
    """
    Simple LULESH runtime plot
    """
    if not exists(PLOTS_ROOT):
        makedirs(PLOTS_ROOT)

    filenames = listdir(RESULTS_DIR)
    filenames.sort()

    results = list()
    for f in filenames:
        t = f.replace("lulesh_wasm_", "")
        t = t.replace(".csv", "")

        # Read in the file
        file_path = join(RESULTS_DIR, f)
        a = list()
        r = list()
        with open(file_path, "r") as fh:
            for line in fh:
                if line.startswith("Threads"):
                    continue

                if not line.strip():
                    continue

                parts = line.split(",")
                a.append(float(parts[2]))
                r.append(float(parts[3]))

        result = (int(t), np.median(a), np.median(r), np.median(r))
        results.append(result)

    results.sort(key=lambda x: x[0])
    for r in results:
        print("{} threads {}s".format(r[0], r[2]))

    x = [r[0] for r in results]
    y = [r[2] for r in results]
    e = [r[3] for r in results]
    plt.errorbar(x, y, yerr=e, label="Faabric")

    ax = plt.gca()
    ax.set_ylabel("Runtime (s)")

    plt.tight_layout()
    plt.savefig(SIMPLE_PLOT_FILE, format="png")

    if not headless:
        plt.show()
