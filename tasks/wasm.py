from invoke import task


@task(default=True)
def build(ctx):
    print("This would be the wasm build")
