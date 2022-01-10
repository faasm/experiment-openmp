from invoke import Collection

from . import container
from . import lulesh
from . import native
from . import run
from . import wasm

ns = Collection(
    container,
    lulesh,
    native,
    run,
    wasm,
)
