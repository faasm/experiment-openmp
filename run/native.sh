#!/bin/bash

set -e

pushd third-party/covid-sim/build

./src/CovidSim

popd
