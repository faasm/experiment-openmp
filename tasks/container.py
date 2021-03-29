from invoke import task
from util import PROJ_ROOT
from os import environ
from copy import copy
from subprocess import run

IMAGE_NAME = "experiment-covid-native"
VERSION = "0.0.1"


@task(default=True)
def build(ctx, nocache=False, push=False):
    shell_env = copy(environ)
    shell_env["DOCKER_BUILDKIT"] = "1"

    img_tag = "-t faasm/{}:{}".format(IMAGE_NAME, VERSION)

    cmd = [
        "docker",
        "build",
        "--nocache" if nocache else "",
        img_tag,
        "--build-arg EXPERIMENTS_VERSION={}".format(VERSION),
    ]

    cmd_str = " ".join(cmd)
    run(cmd_str, shell=True, check=True, cwd=PROJ_ROOT)

    if push:
        run("docker push {}".format(img_tag), check=True, shell=True)
