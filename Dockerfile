FROM faasm/cpp-sysroot:0.1.6

# Clone the code
RUN git clone https://github.com/faasm/experiment-openmp /code/experiment-openmp
WORKDIR /code/experiment-openmp
RUN git submodule update --init

# Install python deps
RUN pip3 install -r requirements.txt

# Prepare data
RUN inv covid.native.unzip

# WebAssembly builds
RUN inv covid.wasm
RUN inv lulesh.build.wasm

# Native build
RUN inv covid.native
RUN inv lulesh.build.native

CMD /code/experiment-openmp/bin/entrypoint.sh
