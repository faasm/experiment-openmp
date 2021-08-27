#!/bin/bash

set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJ_ROOT=${THIS_DIR}/..

pushd ${PROJ_ROOT} > /dev/null

export VERSION=$(cat VERSION)

if [[ -z "$FAASM_LOCAL_DIR" ]]; then
    echo "You must set your local /usr/local/faasm dir through FAASM_LOCAL_DIR"
    exit 1
fi

if [[ -z "$COVID_CLI_IMAGE" ]]; then
    export COVID_CLI_IMAGE=faasm/experiment-covid:${VERSION}
fi

INNER_SHELL=${SHELL:-"/bin/bash"}

docker-compose \
    run \
    --rm \
    covid-cli \
    ${INNER_SHELL}

popd > /dev/null
