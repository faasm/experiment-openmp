ARG EXPERIMENTS_VERSION

FROM faasm/experiment-base-native:${EXPERIMENTS_VERSION}

RUN apt update

WORKDIR /code
RUN git clone https://github.com/faasm/experiment-covid

# Build native 
WORKDIR /code/experiment-covid/
RUN ./build/native.sh

CMD ["/bin/bash"]
