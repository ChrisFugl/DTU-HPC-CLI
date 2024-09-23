from typing import List
from typing import Optional

import typer
from typing_extensions import Annotated

from dtu_hpc_cli.config import Config
from dtu_hpc_cli.list import execute_list
from dtu_hpc_cli.run import execute_run
from dtu_hpc_cli.submit import Feature
from dtu_hpc_cli.submit import Model
from dtu_hpc_cli.submit import Queue
from dtu_hpc_cli.submit import SubmitConfig
from dtu_hpc_cli.submit import execute_submit
from dtu_hpc_cli.types import Memory
from dtu_hpc_cli.types import Time

cli = typer.Typer(pretty_exceptions_show_locals=False)


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


# TODO: add outfile and error files


@cli.command()
def submit(
    commands: List[str],
    branch: str = "main",
    cores: int = 4,
    feature: Annotated[Optional[List[Feature]], typer.Option()] = None,
    gpus: int | None = None,
    hosts: int = 1,
    memory: Annotated[Memory, typer.Option(parser=Memory.parse)] = "5gb",
    model: Model | None = None,
    name: str = "NONAME",
    queue: Queue = Queue.hpc,
    split_every: Annotated[Time, typer.Option(parser=Time.parse)] = "1d",
    start_after: str | None = None,
    walltime: Annotated[Time, typer.Option(parser=Time.parse)] = "1d",
):
    if cores < 1:
        raise typer.BadParameter("cores must be greater than 0")

    if gpus is not None and gpus < 1:
        raise typer.BadParameter("gpus must be greater than 0")

    config = Config.load()

    submit_config = SubmitConfig(
        branch=branch,
        commands=commands,
        cores=cores,
        features=feature,
        error=None,
        gpus=gpus,
        hosts=hosts,
        model=model,
        output=None,
        queue=queue,
        memory=memory,
        name=name,
        split_every=split_every,
        walltime=walltime,
        start_after=start_after,
    )

    execute_submit(config, submit_config)


if __name__ == "__main__":
    cli()
