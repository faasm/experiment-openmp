from glob import glob
from invoke import task
from os import makedirs, listdir
from os.path import join, exists

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from tasks.util import PLOTS_FORMAT, PLOTS_ROOT, PROJ_ROOT

RESULTS_DIR = join(PROJ_ROOT, "results")
PLOTS_DIR = join(PLOTS_ROOT, "lulesh")
RUNTIME_PLOT_FILE = join(PLOTS_DIR, "runtime.{}".format(PLOTS_FORMAT))
SIMPLE_PLOT_FILE = join(PLOTS_DIR, "lulesh.png")


def _read_results(mode):
    result_dict = {}

    for csv in glob(join(RESULTS_DIR, "lulesh_{}_*.csv".format(mode))):
        results = pd.read_csv(csv)

        num_thread = int(csv.split("_")[-1].split(".")[0])

        if mode == "native":
            result_dict[num_thread] = [
                results["Time"].mean(),
                results["Time"].sem(),
            ]
        else:
            result_dict[num_thread] = [
                results["Reported"].mean(),
                results["Reported"].sem(),
            ]

    return result_dict


@task(default=True)
def plot(ctx, headless=False):
    """
    Plot LULESH figure
    """
    makedirs(PLOTS_DIR, exist_ok=True)

    # Load results
    native_results = _read_results("native")
    wasm_results = _read_results("wasm")

    fig, ax = plt.subplots()

    # Plot results - native
    x = list(native_results.keys())
    x.sort()
    y = [native_results[xs][0] for xs in x]
    yerr = [native_results[xs][1] for xs in x]
    ax.errorbar(x, y, yerr=yerr, fmt=".-")

    # Plot results - wasm
    x_wasm = list(wasm_results.keys())
    x_wasm.sort()
    y_wasm = [wasm_results[xs][0] for xs in x_wasm]
    yerr_wasm = [wasm_results[xs][1] for xs in x_wasm]
    ax.errorbar(x_wasm, y_wasm, yerr=yerr_wasm, fmt=".-")

    # Prepare legend
    ax.legend(["OpenMP", "Faabric"], loc="upper left")

    # Aesthetics
    ax.set_ylabel("Elapsed time [s]")
    ax.set_xlabel("# of parallel functions")
    ax.set_ylim(0)
    ax.set_xlim(0, 32)

    fig.tight_layout()

    if headless:
        plt.gca().set_aspect(0.1)
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
    if not exists(PLOTS_DIR):
        makedirs(PLOTS_DIR)

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
