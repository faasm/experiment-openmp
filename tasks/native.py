from invoke import task
from tasks.util import COVID_DIR, BUILD_DIR, DATA_DIR
from os import makedirs
from os.path import exists, join
from shutil import rmtree
from subprocess import run


@task(default=True)
def build(ctx, clean=False):
    """
    Build the native binary
    """
    if clean and exists(BUILD_DIR):
        rmtree(BUILD_DIR)

    makedirs(BUILD_DIR, exist_ok=True)

    run(
        "cmake -G Ninja {}".format(COVID_DIR),
        shell=True,
        check=True,
        cwd=BUILD_DIR,
    )

    run("cmake --build . --target all", shell=True, check=True, cwd=BUILD_DIR)


@task
def unzip(ctx):
    """
    Unzip compressed data from the Covid repo
    """
    files = [
        "wpop_eur.txt",
        "wpop_nga_adm1.txt",
        "wpop_us_terr.txt",
        "wpop_usacan.txt",
    ]

    pop_dir = join(DATA_DIR, "populations")

    for f in files:
        if exists(f):
            print("Skipping {}, already unzipped".format(f))
            continue

        run(
            "gunzip -c {}.gz > {}".format(f, f),
            shell=True,
            check=True,
            cwd=pop_dir,
        )
