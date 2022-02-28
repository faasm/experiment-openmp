FROM faasm/cpp-sysroot:0.1.3

# Clone the code
RUN git clone -b lulesh-2 https://github.com/faasm/experiment-openmp /code/experiment-openmp
WORKDIR /code/experiment-openmp
RUN git submodule update --init

# Install python deps
RUN pip3 install -r requirements.txt

# Prepare data
RUN inv native.unzip

# WebAssembly build
RUN inv wasm

# Native build
RUN inv native

# Build lulesh
RUN inv lulesh.native

CMD /code/experiment-openmp/bin/entrypoint.sh
