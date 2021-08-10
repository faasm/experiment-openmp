# Faasm Covid Experiment

Based on the [Covid microsimulation](https://github.com/mrc-ide/covid-sim) from
ICL.

For general info on running these experiments see the [`experiment-base`
repo](https://github.com/faasm/experiment-base).

## Running on Faasm

The code must be built, and data uploaded, from within the experiment container:

```bash
./bin/cli.sh
```

Unzip and upload the data with:

```bash
inv native.unzip

# Upload Locally
inv run.upload-data --local

# Upload Remotely
inv run.upload-data --host <faasm_upload_host>
```

Build the code with:

```bash
# wasm
inv wasm
```

Upload with:

```bash
inv wasm.upload --host <faasm_upload_host>
```

The experiment must be run from _outside_ the container, using the
`experiment-base` environment:

```bash
inv run.faasm --host=<faasm_invoke_host> --port=<faasm_invoke_port>
```

## Running natively

To run the native version locally, you can build the code within the container:

```bash
./bin/cli.sh

inv native
```

Then run with:

```bash
# Default country
inv run.native

# Some other country
inv run.native --country=Malta
```

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
