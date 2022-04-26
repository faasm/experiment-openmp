#!/bin/bash

set -e

sudo apt install python3-dev python3-pip -y
sudo pip3 install -U pip

git submodule update --init

python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

export FAASM_LOCAL_DIR=${HOME}/code/faasm/dev/faasm-local
mkdir -p ${FAASM_LOCAL_DIR}

echo "export FAASM_LOCAL_DIR=${FAASM_LOCAL_DIR}" >> ~/.bashrc

inv -l
