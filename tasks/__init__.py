from invoke import Collection

from . import container
from . import native
from . import run
from . import wasm

ns = Collection(
    container,
    native,
    run,
    wasm,
    )
