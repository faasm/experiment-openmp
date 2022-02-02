from invoke import Collection

from . import build
from . import plot
from . import run

ns = Collection(build, plot, run)
