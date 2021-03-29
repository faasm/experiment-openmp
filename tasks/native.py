from invoke import task
from tasks.util import COVID_DIR
from os import makedirs
from os.path import exists
from shutil import rmtree
from subprocess import run

BUILD_DIR = "/build/experiment"


@task(default=True)
def build(ctx, clean=False):
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
