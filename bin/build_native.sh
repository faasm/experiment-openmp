#!/bin/bash

set -e

pushd third-party/covid-sim

mkdir -p build

pushd build

cmake .. -G Ninja

cmake --build . --target all

popd

popd
