ARG EXPERIMENTS_VERSION
FROM faasm/cpp-sysroot:0.0.22 as toolchain

ARG EXPERIMENTS_VERSION
FROM faasm/experiment-base:${EXPERIMENTS_VERSION} as experiments

# Copy in toolchain
COPY --from=toolchain /usr/local/faasm /usr/local/faasm

# Clone the code
RUN git clone https://github.com/faasm/experiment-covid /code/experiment-covid
WORKDIR /code/experiment-covid
RUN git checkout wasm-build
RUN git submodule update --init

# Unzip and copy population files
WORKDIR /code/experiment-covid/third-party/covid-sim/data/populations
RUN gunzip -c wpop_us_terr.txt.gz > /tmp/wpop_us_terr.txt 
RUN gunzip -c wpop_eur.txt.gz > /tmp/wpop_eur.txt 
RUN gunzip -c wpop_usacan.txt.gz > /tmp/wpop_usacan.txt 
WORKDIR /code/experiment-covid

# WebAssembly build
RUN inv wasm

# Native build
RUN inv native

CMD ["/bin/bash"]
