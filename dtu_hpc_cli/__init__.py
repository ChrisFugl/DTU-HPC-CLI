import typer

from dtu_hpc_cli.config import Config
from dtu_hpc_cli.list import run_list

cli = typer.Typer()


@cli.command()
def list():
    config = Config.load()
    run_list(config)


@cli.command()
def run():
    print("run")


@cli.command()
def submit():
    print("submit")


if __name__ == "__main__":
    cli()
