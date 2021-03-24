ARG EXPERIMENTS_VERSION

FROM faasm/experiment-base-native:${EXPERIMENTS_VERSION}

RUN apt update

WORKDIR /code
RUN git clone -b native https://github.com/faasm/experiment-covid

# Build native 
WORKDIR /code/experiment-covid/
RUN git submodule update --init
RUN ./build/native.sh

# Prepare the entrypoint
ENTRYPOINT ["/code/experiment-covid/run/single_native.py"]
