ARG EXPERIMENTS_VERSION

FROM faasm/cpp-sysroot:0.0.22 as build-step

# Clone the code
RUN git clone https://github.com/faasm/experiment-covid /code/experiment
RUN git submodule update --init
WORKDIR /code/experiment

# WebAssembly build
RUN ./build/wasm.sh

# New container from experiments-base
FROM faasm/experiment-base:${EXPERIMENTS_VERSION} as experiments

RUN apt update

# Copy in artifacts from build
COPY --from=build-step /code/experiment /code/experiment

# Native build
RUN ./build/native.sh

# Unzip and copy population files
WORKDIR /code/experiment/third-party/covid-sim/data/populations
RUN gunzip -c wpop_us_terr.txt.gz > /tmp/wpop_us_terr.txt 
RUN gunzip -c wpop_eur.txt.gz > /tmp/wpop_eur.txt 
RUN gunzip -c wpop_usacan.txt.gz > /tmp/wpop_usacan.txt 
WORKDIR /code/experiment

CMD ["/bin/bash"]
