from typing import List
from typing import Optional

import typer
from typing_extensions import Annotated

from dtu_hpc_cli.config import Config
from dtu_hpc_cli.constants import CONFIG_FILENAME
from dtu_hpc_cli.install import execute_install
from dtu_hpc_cli.list import ListConfig
from dtu_hpc_cli.list import ListStats
from dtu_hpc_cli.list import execute_list
from dtu_hpc_cli.remove import execute_remove
from dtu_hpc_cli.run import execute_run
from dtu_hpc_cli.submit import Feature
from dtu_hpc_cli.submit import Model
from dtu_hpc_cli.submit import Queue
from dtu_hpc_cli.submit import SubmitConfig
from dtu_hpc_cli.submit import execute_submit
from dtu_hpc_cli.sync import execute_sync
from dtu_hpc_cli.types import Memory
from dtu_hpc_cli.types import Time

cli = typer.Typer(pretty_exceptions_show_locals=False)


@cli.command()
def history():
    # TODO
    pass


@cli.command()
def install():
    cli_config = Config.load()
    execute_install(cli_config)


@cli.command()
def list(
    node: str | None = None,
    queue: str | None = None,
    stats: Annotated[ListStats, typer.Option()] = None,
):
    cli_config = Config.load()
    list_config = ListConfig(node=node, queue=queue, stats=stats)
    execute_list(cli_config, list_config)


@cli.command()
def remove(job_ids: List[str]):
    config = Config.load()
    execute_remove(config, job_ids)


@cli.command()
def resubmit():
    # TODO
    pass


@cli.command()
def run(commands: List[str]):
    config = Config.load()
    execute_run(config, commands)


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


@cli.command()
def sync():
    cli_config = Config.load()
    cli_config.check_ssh(msg=f"Sync requires a SSH configuration in '{CONFIG_FILENAME}'.")
    execute_sync(cli_config)


if __name__ == "__main__":
    cli()
