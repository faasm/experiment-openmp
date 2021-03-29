ARG EXPERIMENTS_VERSION

FROM faasm/cpp-sysroot:0.0.22 as build-step

RUN git clone https://github.com/faasm/experiment-covid /code/experiment
WORKDIR /code/experiment
RUN git submodule update --init

FROM faasm/experiment-base:${EXPERIMENTS_VERSION} as experiments

COPY --from=build-step /code/experiment-lammps /code/experiment-lammps

FROM faasm/cli:0.5.10

RUN apt update

COPY . /code/experiment/

# Build native 
WORKDIR /code/experiment/
RUN ./bin/build_native.sh

# Build wasm version
RUN ./bin/build_wasm.sh

CMD ["/bin/bash"]
