from invoke import Collection

from . import wasm
from . import native
from . import plot
from . import run

ns = Collection(wasm,native,plot, run)
