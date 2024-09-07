from typing import List

import typer

from dtu_hpc_cli.config import Config
from dtu_hpc_cli.list import execute_list
from dtu_hpc_cli.run import execute_run

cli = typer.Typer()


@cli.command()
def list():
    config = Config.load()
    execute_list(config)


@cli.command()
def run(commands: List[str]):
    config = Config.load()
    execute_run(config, commands)


@cli.command()
def remove():
    # TODO
    print("remove")


@cli.command()
def submit():
    # TODO
    print("submit")


if __name__ == "__main__":
    cli()
