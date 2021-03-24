#!/bin/bash

set -e

pushd third-party/covid-sim/build

./src/CovidSim

./run_sample.py Guam --covidsim /build/experiment/ src/CovidSim --threads 1

popd
