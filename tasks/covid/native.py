from invoke import task
from tasks.util import COVID_DIR, NATIVE_BUILD_DIR, DATA_DIR
from os import makedirs, listdir
from os.path import exists, join
from shutil import rmtree
from subprocess import run


@task(default=True)
def build(ctx, clean=False):
    """
    Build the native binary
    """
    if clean and exists(NATIVE_BUILD_DIR):
        rmtree(NATIVE_BUILD_DIR)

    makedirs(NATIVE_BUILD_DIR, exist_ok=True)

    cmake_cmd = [
        "cmake",
        "-G Ninja",
        "-DCMAKE_BUILD_TYPE=Release",
        COVID_DIR,
    ]

    run(
        " ".join(cmake_cmd),
        shell=True,
        check=True,
        cwd=NATIVE_BUILD_DIR,
    )

    run(
        "cmake --build . --target all",
        shell=True,
        check=True,
        cwd=NATIVE_BUILD_DIR,
    )


@task
def countries(ctx):
    """
    List the countries supported by the simulation
    """
    admin_dir = join(DATA_DIR, "admin_units")
    admin_files = listdir(admin_dir)

    countries = list()

    for f in admin_files:
        country = f.replace("_admin.txt", "")
        admin_file = join(admin_dir, f)

        try:
            with open(admin_file, "rb") as fh:
                next_line = False
                for line in fh:
                    if b"[Population size]" in line:
                        next_line = True
                        continue

                    if next_line:
                        line_str = line.decode("utf-8")
                        population = int(line_str.strip())
                        fh.close()
                        break
        except UnicodeDecodeError:
            print("Can't read {}".format(f))
            continue

        countries.append((country, population))

    countries.sort(key=lambda x: x[1])

    for c, p in countries:
        print("{} : {}".format(c, p))


@task
def unzip(ctx):
    """
    Unzip compressed data from the Covid repo
    """
    files = [
        "wpop_eur.txt",
        "wpop_nga_adm1.txt",
        "wpop_us_terr.txt",
        "wpop_usacan.txt",
    ]

    pop_dir = join(DATA_DIR, "populations")

    for f in files:
        if exists(f):
            print("Skipping {}, already unzipped".format(f))
            continue

        run(
            "gunzip -c {}.gz > {}".format(f, f),
            shell=True,
            check=True,
            cwd=pop_dir,
        )
