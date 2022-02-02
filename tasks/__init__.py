from invoke import Collection

from . import container

import logging

from tasks.covid import ns as covid_ns
from tasks.lulesh import ns as lulesh_ns

logging.getLogger().setLevel(logging.DEBUG)

ns = Collection(
    container,
)

ns.add_collection(lulesh_ns, name="lulesh")
ns.add_collection(covid_ns, name="covid")
