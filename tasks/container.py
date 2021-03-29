from invoke import task
from tasks.util import PROJ_ROOT, get_experiments_base_version
from os import environ
from copy import copy
from subprocess import run

IMAGE_NAME = "experiment-covid"


@task(default=True)
def build(ctx, nocache=False, push=False):
    shell_env = copy(environ)
    shell_env["DOCKER_BUILDKIT"] = "1"

    base_ver = get_experiments_base_version()

    img_tag = "faasm/{}:{}".format(IMAGE_NAME, base_ver)

    cmd = [
        "docker",
        "build",
        "--nocache" if nocache else "",
        "--build-arg EXPERIMENTS_VERSION={}".format(base_ver),
        "-t {}".format(img_tag),
        ".",
    ]

    cmd_str = " ".join(cmd)
    print(cmd_str)
    run(cmd_str, shell=True, check=True, cwd=PROJ_ROOT)

    if push:
        run("docker push {}".format(img_tag), check=True, shell=True)
