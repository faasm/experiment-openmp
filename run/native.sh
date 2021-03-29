#!/bin/bash

set -e

THIS_DIR=$(dirname $(readlink -f $0))
PROJ_ROOT=${THIS_DIR}/..
PLOT_DIR=${PROJ_ROOT}/../../results/covid

pushd ${PROJ_ROOT} >> /dev/null

# Run the experiment
python3 ./run/all_native.py

pushd ${PLOT_DIR} >> /dev/null

# Plot the results
python3 plot.py

popd >> /dev/null

popd >> /dev/null

