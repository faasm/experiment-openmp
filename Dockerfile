FROM faasm/cpp-sysroot:0.0.26

# Install hoststats
RUN pip3 install hoststats

# Clone the code
RUN git clone https://github.com/faasm/experiment-covid /code/experiment-covid
WORKDIR /code/experiment-covid
RUN git submodule update --init

# Prepare data
RUN inv native.unzip

# WebAssembly build
RUN inv wasm

# Native build
RUN inv native

CMD /code/experiment-covid/bin/entrypoint.sh
