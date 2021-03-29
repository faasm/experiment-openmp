from invoke import task


@task(default=True)
def build(ctx):
    """
    Builds the function for Faasm
    """
    print("This would be the wasm build")
