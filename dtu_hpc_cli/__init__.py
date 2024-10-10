from typing import List

import typer
from typing_extensions import Annotated

from dtu_hpc_cli.config import Feature
from dtu_hpc_cli.config import Model
from dtu_hpc_cli.config import Queue
from dtu_hpc_cli.config import SubmitConfig
from dtu_hpc_cli.config import cli_config
from dtu_hpc_cli.constants import CONFIG_FILENAME
from dtu_hpc_cli.install import execute_install
from dtu_hpc_cli.list import ListConfig
from dtu_hpc_cli.list import ListStats
from dtu_hpc_cli.list import execute_list
from dtu_hpc_cli.remove import execute_remove
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
    execute_install()


@cli.command()
def list(
    node: str | None = None,
    queue: str | None = None,
    stats: Annotated[ListStats, typer.Option()] = None,
):
    list_config = ListConfig(node=node, queue=queue, stats=stats)
    execute_list(list_config)


@cli.command()
def remove(job_ids: List[str]):
    execute_remove(job_ids)


@cli.command()
def resubmit():
    # TODO
    pass


class SubmitDefault:
    def __init__(self, key: str):
        self.value = cli_config.submit.get(key)

    def __call__(self):
        return self.value

    def __str__(self):
        return str(self.value)


@cli.command()
def submit(
    commands: List[str],
    branch: Annotated[str, typer.Option(default_factory=SubmitDefault("branch"))],
    cores: Annotated[int, typer.Option(default_factory=SubmitDefault("cores"))],
    error: Annotated[str, typer.Option(default_factory=SubmitDefault("error"))],
    feature: Annotated[List[Feature], typer.Option(default_factory=SubmitDefault("feature"))],
    gpus: Annotated[int, typer.Option(default_factory=SubmitDefault("gpus"))],
    hosts: Annotated[int, typer.Option(default_factory=SubmitDefault("hosts"))],
    memory: Annotated[Memory, typer.Option(parser=Memory.parse, default_factory=SubmitDefault("memory"))],
    model: Annotated[Model, typer.Option(default_factory=SubmitDefault("model"))],
    name: Annotated[str, typer.Option(default_factory=SubmitDefault("name"))],
    output: Annotated[str, typer.Option(default_factory=SubmitDefault("output"))],
    preamble: Annotated[List[str], typer.Option(default_factory=SubmitDefault("preamble"))],
    queue: Annotated[Queue, typer.Option(default_factory=SubmitDefault("queue"))],
    split_every: Annotated[Time, typer.Option(parser=Time.parse, default_factory=SubmitDefault("split_every"))],
    start_after: Annotated[str, typer.Option(default_factory=SubmitDefault("start_after"))],
    walltime: Annotated[Time, typer.Option(parser=Time.parse, default_factory=SubmitDefault("walltime"))],
):
    submit_config = SubmitConfig(
        commands=commands,
        branch=branch,
        cores=cores,
        error=error,
        feature=feature,
        gpus=gpus,
        hosts=hosts,
        memory=memory,
        model=model,
        name=name,
        output=output,
        preamble=preamble,
        queue=queue,
        split_every=split_every,
        start_after=start_after,
        walltime=walltime,
    )
    execute_submit(submit_config)


@cli.command()
def sync():
    cli_config.check_ssh(msg=f"Sync requires a SSH configuration in '{CONFIG_FILENAME}'.")
    execute_sync()


if __name__ == "__main__":
    cli()
