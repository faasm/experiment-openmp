# Faasm Covid Experiment

Based on the [Covid microsimulation](https://github.com/mrc-ide/covid-sim) from
ICL. 

This repository should be used as a submodule of 
[faasm/experiment-base](https://github.com/faasm/experiment-base).

The container image used for these experiments is
[`faasm/experiment-covid`](https://hub.docker.com/repository/docker/faasm/experiment-lammps).

## Commandline

```
# Build the container
inv container

# Build to wasm
inv wasm

# Build native
inv native
```

## Example Invocation

Whilst the experiment is under development, nice to have a reminder of a sample
command line invocation of the simulator:
```
/build/experiment/src/CovidSim \
      /c:1 \
      /A:/code/experiment-covid/third-party/covid-sim/data/admin_units/Virgin_Islands_US_admin.txt \
      /PP:/code/experiment-covid/third-party/covid-sim/data/param_files/preUK_R0=2.0.txt \
      /P:/code/experiment-covid/third-party/covid-sim/data/param_files/p_NoInt.txt \
      /O:/tmp/Virgin_Islands_US_NoInt_R0=3.0 \
      /D:/tmp/wpop_us_terr.txt \
      /M:/tmp/Virgin_Islands_US_pop_density.bin \
      /S:/tmp/Network_Virgin_Islands_US_T1_R3.0.bin \
      /R:1.5 98798150 729101 17389101 4797132
```

