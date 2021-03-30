ARG EXPERIMENTS_VERSION
FROM faasm/cpp-sysroot:0.0.23 as toolchain

ARG EXPERIMENTS_VERSION
FROM faasm/experiment-base:${EXPERIMENTS_VERSION} as experiments

# Copy in toolchain
COPY --from=toolchain /usr/local/faasm /usr/local/faasm

# Clone the code
RUN git clone https://github.com/faasm/experiment-covid /code/experiment-covid
WORKDIR /code/experiment-covid
RUN git checkout wasm-build
RUN git submodule update --init

# Prepare data
RUN inv native.unzip

# WebAssembly build
RUN inv wasm

# Native build
RUN inv native

CMD ["/bin/bash"]
