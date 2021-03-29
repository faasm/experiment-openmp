from invoke import task
from util import PROJ_ROOT, COVID_DIR
from os import exists
from shutil import rmtree

BUILD_DIR = "/build/experiment"


@task
def build(ctx, clean=False):
    if clean and exists(BUILD_DIR):
        rmtree(BUILD_DIR)

    makedirectories(BUILD_DIR, exist_ok=True)

    run("cmake -G Ninja {}".format(COVID_DIR), shell=True, check=True, cwd=BUILD_DIR)

    run("cmake --build . --target all", shell=True, check=True, cwd=BUILD_DIR)
