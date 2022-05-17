FROM faasm/cpp-sysroot:0.2.0

# Clone the code
RUN git clone https://github.com/faasm/experiment-openmp /code/experiment-openmp
WORKDIR /code/experiment-openmp
RUN git checkout azure-260422
RUN git submodule update --init

# Install python deps
RUN pip3 install -r requirements.txt

# WebAssembly builds
RUN inv lulesh.build.wasm
RUN inv kernels.build.wasm

# Native build
RUN inv lulesh.build.native
RUN inv kernels.build.native

CMD /code/experiment-openmp/bin/entrypoint.sh
