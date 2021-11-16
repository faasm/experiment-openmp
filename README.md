# Faasm Covid Experiment

Based on the [Covid microsimulation](https://github.com/mrc-ide/covid-sim) from
ICL.

Note, this repo should be checked out as part of the Faasm/ Faabric experiment
set-up covered in the [`experiment-base`
repo](https://github.com/faasm/experiment-base).

To check things are working:

```bash
../../bin/workon.sh

inv -l
```

## Running on Faasm

The code must be built from within the experiment container:

```bash
./bin/cli.sh

inv wasm
```

The experiment can then be set up and run from _outside_ the container:

```bash
source ../../bin/workon.sh

# Data
inv native.unzip
inv run.upload-data

# Wasm
inv wasm.upload

# Run
inv run.faasm
```

### Local dev setup

To run against a local development cluster, set one up according to the
[docs](https://github.com/faasm/faasm/blob/master/docs/development.md).

Make sure your local `faasm.ini` file is then updated to run locally:

```bash
# In faasm-cli
inv knative.ini-file --local
```

## Running natively

To run the native version locally, you can build the code within the container:

```bash
./bin/cli.sh

inv native
```

Then run (also inside the container):

```bash
# Default country
inv run.native

# Some other country
inv run.native --country=Malta
```

Remember that as this is based on OpenMP, the native version cannot run in a
distributed manner.

## Rebuilding the container

You can rebuild the image with:

```bash
inv container
```

## Example Invocation

The commandline arguments for the CovidSim executable are quite long and fiddly.
Included here a couple of working examples for reference (the tasks in this repo
will generate the relevant arguments automatically).

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
