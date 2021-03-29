#!/bin/bash

set -e

THIS_DIR=$(dirname $(readlink -f $0))
PROJ_ROOT=${THIS_DIR}/..
DOCKER_DIR=${PROJ_ROOT}/docker
BASE_DIR=${PROJ_ROOT}/../..
COVID_DIR=${PROJ_ROOT}/third-party/covid-sim

IMAGE_NAME="experiment-covid-native"
VERSION="$(< ${BASE_DIR}/VERSION)"

pushd ${PROJ_ROOT} >> /dev/null

export DOCKER_BUILDKIT=1

# Docker args
if [ "$1" == "--no-cache" ]; then
    NO_CACHE=$1
else
    NO_CACHE=""
fi

docker build \
    ${NO_CACHE} \
    -t faasm/${IMAGE_NAME}:${VERSION} \
    -f ${DOCKER_DIR}/${IMAGE_NAME}.dockerfile \
    --build-arg EXPERIMENTS_VERSION=${VERSION} \
    ${PROJ_ROOT}

if [ "${BASH_ARGV[0]}" == "--push" ]; then
    docker push faasm/${IMAGE_NAME}:${VERSION}
fi

popd >> /dev/null

