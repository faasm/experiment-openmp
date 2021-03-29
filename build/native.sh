#!/bin/bash

set -e

PROJ_ROOT=/code/experiment-covid
COVID_DIR=${PROJ_ROOT}/third-party/covid-sim
BUILD_DIR=/build/experiment

mkdir -p ${BUILD_DIR}

pushd ${BUILD_DIR} >> /dev/null

cmake ${COVID_DIR} -G Ninja

cmake --build . --target all

popd >> /dev/null

