# Faasm OpenMP Experiments

Instructions and scripts for setting up Kubernetes and VMs can be found in the
[`experiment-base` repo](https://github.com/faasm/experiment-base).

To set up locally, from the root of this project:

```bash
./bin/local_setup.sh

# Log out and log in again for permissions
```

## Local dev setup

To run against a local Faasm development cluster, set one up according to the
[docs](https://faasm.readthedocs.io/en/latest/source/development.html).

Make sure your local `faasm.ini` file is then updated to run locally:

```bash
# In faasm-cli
inv knative.ini-file --local
```

## Rebuilding the container

You should only need to rebuild the container if you're adding an experiment or
changing something related to compiling applications for Faasm.

If you do need to, you can do so with:

```bash
inv container
```

## Running experiments on a single VM

To run the baselines for each experiment, we must run it on a single VM of the
same type as the node pool underlying the K8s cluster used to execute Faasm.

It's recommended that you set up the VM using the instructions in the
[`experiment-base` repo](https://github.com/faasm/experiment-base).

Once you have a VM set up with the code from this repo, you can run the
experiment-specific commands.

## LULESH

Runs [LULESH](https://github.com/LLNL/LULESH).

### Running natively

```bash
./bin/cli.sh

inv lulesh.build.native

inv lulesh.run.native
```

### Running on Faasm

```bash
./bin/cli.sh

inv lulesh.build.wasm

inv lulesh.build.upload

inv lulesh.run.faasm
```

## ParRes Kernels (OpenMP)

Runs OpenMP kernels from [ParRes Kernels](https://github.com/ParRes/Kernels).

### Running natively

```bash
./bin/cli.sh

inv kernels.build.native

inv kernels.run.native
```

### Running on Faasm

```bash
./bin/cli.sh

inv kernels.build.wasm

inv kernels.build.upload

inv kernels.run.faasm
```

## Covid Sim

Based on the [Covid microsimulation](https://github.com/mrc-ide/covid-sim) from
ICL.

### Countries

To list which countries are available and what their populations are:

```bash
inv covid.native.unzip
inv covid.native.countries
```

### Running on Faasm

The code must be built from within the experiment container:

```bash
./bin/cli.sh

inv covid.wasm
```

The experiment can then be set up and run from _outside_ the container:

```bash
source ../../bin/workon.sh

# Data
inv covid.native.unzip
inv covid.run.upload-data

# Wasm
inv covid.wasm.upload

# Run
inv covid.run.faasm
```

### Running natively

To run the native version locally, you can build the code within the container:

```bash
./bin/cli.sh

inv covid.native
```

Then run (also inside the container):

```bash
# Default country
inv covid.run.native

# Some other country
inv covid.run.native --country=Malta
```

Remember that as this is based on OpenMP, the native version cannot run in a
distributed manner.

### Example Invocation

The commandline arguments for the CovidSim executable are quite long and fiddly.
Included here a couple of working examples for reference (the tasks in this repo
will generate the relevant arguments automatically).

**Native** for US Virgin Islands

```
/build/experiment/src/CovidSim \
      /c:1 \
      /A:/code/experiment-openmp/third-party/covid-sim/data/admin_units/Virgin_Islands_US_admin.txt \
      /PP:/code/experiment-openmp/third-party/covid-sim/data/param_files/preUK_R0=2.0.txt \
      /P:/code/experiment-openmp/third-party/covid-sim/data/param_files/p_NoInt.txt \
      /O:/tmp/Virgin_Islands_US_NoInt_R0=3.0 \
      /D:/tmp/wpop_us_terr.txt \
      /M:/tmp/Virgin_Islands_US_pop_density.bin \
      /S:/tmp/Network_Virgin_Islands_US_T1_R3.0.bin \
      /R:1.5 98798150 729101 17389101 4797132
```

**Faasm** for Guam

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
