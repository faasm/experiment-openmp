# Faasm Covid Experiment

Based on the [Covid microsimulation](https://github.com/mrc-ide/covid-sim) from
ICL. 

This repository should be used as a submodule of 
[faasm/experiment-base](https://github.com/faasm/experiment-base).

## Setup

The data must be unzipped using:

```bash
inv native.unzip
```

Then uploaded to Faasm using:

```bash
# Locally
inv run.upload-data --local

# Remotely
inv run.upload-data --host <faasm_host>
```

You can then build the code with:

```bash
inv wasm
```

Which will automatically do the local upload. To upload remotely:

```bash
inv wasm.upload --host <faasm_host>
```

To see what other tasks are available, run:

```bash
inv -l
```

## Running

To run the native version locally, you can call:

```bash
# Default country
inv run.native

# Some other country
inv run.native --country=Malta
```

To run the experiment in Faasm you need a Faasm cluster running somewhere:

```bash
inv run.faasm --host=<faasm_host>
```

## Example Invocation

The commandline arguments for the CovidSim executable are quite long and fiddly,
here are two examples:

### Native

For US Virgin Islands

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

### Faasm

For Guam

```
{
    'user': 'cov', 
    'function': 'sim', 
    'cmdline': '/c:20                                       \
        /A:faasm://covid/admin_units/Guam_admin.txt        \
        /PP:faasm://covid/param_files/preUK_R0=2.0.txt     \
        /P:faasm://covid/param_files/p_NoInt.txt           \
        /O:/tmp/Guam_NoInt_R0=3.0                           \
        /D:/faasm://covid/populations/wpop_us_terr.txt     \
        /M:/tmp/Guam_pop_density.bin                        \
        /S:/tmp/Network_Guam_T1_R3.0.bin                    \
        /R:1.5 98798150 729101 17389101 4797132'
}
```
