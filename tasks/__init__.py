from invoke import Collection

from . import container
from . import lufaasm
from . import lulesh
from . import native
from . import run
from . import wasm

ns = Collection(
    container,
    lufaasm,
    lulesh,
    native,
    run,
    wasm,
)
