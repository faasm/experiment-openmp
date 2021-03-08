FROM faasm/cli:0.5.10

RUN apt update

COPY . /code/experiment/

# Build native 
WORKDIR /code/experiment/
RUN ./bin/build_native.sh

# Build wasm version
RUN ./bin/build_wasm.sh

CMD ["/bin/bash"]
