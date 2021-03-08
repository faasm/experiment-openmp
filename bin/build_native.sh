#!/bin/bash

set -e

PROJ_ROOT=$(pwd)
COVID_DIR=${PROJ_ROOT}/third-party/covid-sim

if [[ -z "$FAASM_DOCKER" ]]; then
    # Non-Docker
    BUILD_DIR=third-party/covid-sim/build
    echo "Non-Dockerised build of ${PROJ_ROOT}"
else
    # Docker
    BUILD_DIR=/build/experiment
    echo "Dockerised build of ${PROJ_ROOT}"
fi

mkdir -p ${BUILD_DIR}

pushd ${BUILD_DIR}

cmake ${COVID_DIR} -G Ninja

cmake --build . --target all

popd
