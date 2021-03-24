ARG EXPERIMENTS_VERSION

FROM faasm/experiment-base-native:${EXPERIMENTS_VERSION}

RUN apt update

WORKDIR /code
RUN git clone -b native https://github.com/faasm/experiment-covid

# Build native 
WORKDIR /code/experiment-covid/
RUN git submodule update --init
RUN ./build/native.sh

# Unzip and copy population files
WORKDIR /code/experiment-covid/third-party/covid-sim/data/populations
RUN gunzip -c wpop_us_terr.txt.gz > /tmp/wpop_us_terr.txt 
RUN gunzip -c wpop_eur.txt.gz > /tmp/wpop_eur.txt 
RUN gunzip -c wpop_usacan.txt.gz > /tmp/wpop_usacan.txt 
WORKDIR /code/experiment-covid

# Prepare the entrypoint
ENTRYPOINT ["/code/experiment-covid/run/single_native.py"]
