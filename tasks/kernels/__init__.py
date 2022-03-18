from invoke import Collection

from . import build
from . import run

ns = Collection(build, run)
