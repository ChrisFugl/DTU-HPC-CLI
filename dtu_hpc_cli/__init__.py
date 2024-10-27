from typing import List

import typer
from typing_extensions import Annotated

from dtu_hpc_cli.config import SubmitConfig
from dtu_hpc_cli.config import cli_config
from dtu_hpc_cli.constants import CONFIG_FILENAME
from dtu_hpc_cli.get_command import execute_get_command
from dtu_hpc_cli.history import HistoryConfig
from dtu_hpc_cli.history import execute_history
from dtu_hpc_cli.install import execute_install
from dtu_hpc_cli.jobs import JobsConfig
from dtu_hpc_cli.jobs import JobsStats
from dtu_hpc_cli.jobs import execute_jobs
from dtu_hpc_cli.queues import execute_queues
from dtu_hpc_cli.remove import RemoveConfig
from dtu_hpc_cli.remove import execute_remove
from dtu_hpc_cli.resubmit import ResubmitConfig
from dtu_hpc_cli.resubmit import execute_resubmit
from dtu_hpc_cli.run import execute_run
from dtu_hpc_cli.start_time import StartTimeConfig
from dtu_hpc_cli.start_time import execute_start_time
from dtu_hpc_cli.stats import StatsConfig
from dtu_hpc_cli.stats import execute_stats
from dtu_hpc_cli.submit import execute_submit
from dtu_hpc_cli.sync import execute_sync
from dtu_hpc_cli.types import Memory
from dtu_hpc_cli.types import Time

cli = typer.Typer(pretty_exceptions_show_locals=False)


@cli.command()
def get_command(job_id: str):
    """Get the command used to submit a previous job."""
    execute_get_command(job_id)


@cli.command()
def history(
    branch: bool = True,
    branch_contains: str | None = None,
    branch_is: str | None = None,
    commands: bool = True,
    command_contains: str | None = None,
    command_is: str | None = None,
    cores: bool = True,
    cores_above: int | None = None,
    cores_below: int | None = None,
    cores_is: int | None = None,
    feature: bool = False,
    feature_contains: str | None = None,
    feature_is: str | None = None,
    error: bool = False,
    error_contains: str | None = None,
    error_is: str | None = None,
    gpus: bool = True,
    gpus_above: int | None = None,
    gpus_below: int | None = None,
    gpus_is: int | None = None,
    hosts: bool = False,
    hosts_above: int | None = None,
    hosts_below: int | None = None,
    hosts_is: int | None = None,
    limit: int = 5,
    memory: bool = True,
    memory_above: Annotated[Memory, typer.Option(parser=Memory.parse)] = None,
    memory_below: Annotated[Memory, typer.Option(parser=Memory.parse)] = None,
    memory_is: Annotated[Memory, typer.Option(parser=Memory.parse)] = None,
    model: bool = False,
    model_contains: str | None = None,
    model_is: str | None = None,
    name: bool = True,
    name_contains: str | None = None,
    name_is: str | None = None,
    output: bool = False,
    output_contains: str | None = None,
    output_is: str | None = None,
    queue: bool = True,
    queue_contains: str | None = None,
    queue_is: str | None = None,
    preamble: bool = False,
    preamble_contains: str | None = None,
    preamble_is: str | None = None,
    split_every: bool = False,
    split_every_above: Annotated[Time, typer.Option(parser=Time.parse)] = None,
    split_every_below: Annotated[Time, typer.Option(parser=Time.parse)] = None,
    split_every_is: Annotated[Time, typer.Option(parser=Time.parse)] = None,
    start_after: bool = False,
    start_after_contains: str | None = None,
    start_after_is: str | None = None,
    walltime: bool = True,
    walltime_above: Annotated[Time, typer.Option(parser=Time.parse)] = None,
    walltime_below: Annotated[Time, typer.Option(parser=Time.parse)] = None,
    walltime_is: Annotated[Time, typer.Option(parser=Time.parse)] = None,
):
    """Show the history of submitted jobs."""
    config = HistoryConfig(
        branch=branch,
        branch_contains=branch_contains,
        branch_is=branch_is,
        commands=commands,
        command_contains=command_contains,
        command_is=command_is,
        cores=cores,
        cores_above=cores_above,
        cores_below=cores_below,
        cores_is=cores_is,
        feature=feature,
        feature_contains=feature_contains,
        feature_is=feature_is,
        error=error,
        error_contains=error_contains,
        error_is=error_is,
        gpus=gpus,
        gpus_above=gpus_above,
        gpus_below=gpus_below,
        gpus_is=gpus_is,
        hosts=hosts,
        hosts_above=hosts_above,
        hosts_below=hosts_below,
        hosts_is=hosts_is,
        limit=limit,
        memory=memory,
        memory_above=memory_above,
        memory_below=memory_below,
        memory_is=memory_is,
        model=model,
        model_contains=model_contains,
        model_is=model_is,
        name=name,
        name_contains=name_contains,
        name_is=name_is,
        output=output,
        output_contains=output_contains,
        output_is=output_is,
        queue=queue,
        queue_contains=queue_contains,
        queue_is=queue_is,
        preamble=preamble,
        preamble_contains=preamble_contains,
        preamble_is=preamble_is,
        split_every=split_every,
        split_every_above=split_every_above,
        split_every_below=split_every_below,
        split_every_is=split_every_is,
        start_after=start_after,
        start_after_contains=start_after_contains,
        start_after_is=start_after_is,
        walltime=walltime,
        walltime_above=walltime_above,
        walltime_below=walltime_below,
        walltime_is=walltime_is,
    )
    execute_history(config)


@cli.command()
def install():
    """Run the install script in the remote directory on the HPC."""
    execute_install()


@cli.command()
def jobs(
    node: str | None = None,
    queue: str | None = None,
    stats: Annotated[JobsStats, typer.Option()] = None,
):
    """List running and pending jobs."""
    list_config = JobsConfig(node=node, queue=queue, stats=stats)
    execute_jobs(list_config)


@cli.command()
def queues(queue: Annotated[str, typer.Argument()] = None):
    """List available queues."""
    execute_queues(queue)


@cli.command()
def remove(job_ids: List[str], from_history: bool = False):
    """Remove jobs from the queue."""
    config = RemoveConfig(from_history=from_history, job_ids=job_ids)
    execute_remove(config)


@cli.command()
def resubmit(
    job_id: str,
    branch: str = None,
    command: List[str] = None,
    cores: int = None,
    error: str = None,
    feature: List[str] = None,
    gpus: int = None,
    hosts: int = None,
    memory: Annotated[Memory, typer.Option(parser=Memory.parse)] = None,
    model: str = None,
    name: str = None,
    output: str = None,
    preamble: List[str] = None,
    queue: str = None,
    split_every: Annotated[Time, typer.Option(parser=Time.parse)] = None,
    start_after: str = None,
    walltime: Annotated[Time, typer.Option(parser=Time.parse)] = None,
):
    """Resubmit a job. Optionally with new parameters."""
    config = ResubmitConfig(
        job_id=job_id,
        branch=branch,
        commands=command,
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
    execute_resubmit(config)


@cli.command()
def run(commands: List[str]):
    """Run one or more commands on the HPC.

    Uses the configured remote path as the working directory."""
    execute_run(commands)


@cli.command()
def start_time(job_ids: Annotated[List[str], typer.Argument()] = None, queue: str = None, user: str = None):
    """Show the start time of pending jobs."""
    config = StartTimeConfig(job_ids=job_ids, queue=queue, user=user)
    execute_start_time(config)


@cli.command()
def stats(
    queue: Annotated[str, typer.Argument()] = None,
    cpu: bool = False,
    gpu: bool = False,
    jobs: bool = False,
    memory: bool = False,
    node: str | None = None,
    reserved: bool = False,
):
    """Show statistics for the queue(s)."""
    config = StatsConfig(
        cpu=cpu,
        gpu=gpu,
        jobs=jobs,
        memory=memory,
        node=node,
        reserved=reserved,
        queue=queue,
    )
    execute_stats(config)


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
    feature: Annotated[List[str], typer.Option(default_factory=SubmitDefault("feature"))],
    gpus: Annotated[int, typer.Option(default_factory=SubmitDefault("gpus"))],
    hosts: Annotated[int, typer.Option(default_factory=SubmitDefault("hosts"))],
    memory: Annotated[Memory, typer.Option(parser=Memory.parse, default_factory=SubmitDefault("memory"))],
    model: Annotated[str, typer.Option(default_factory=SubmitDefault("model"))],
    name: Annotated[str, typer.Option(default_factory=SubmitDefault("name"))],
    output: Annotated[str, typer.Option(default_factory=SubmitDefault("output"))],
    preamble: Annotated[List[str], typer.Option(default_factory=SubmitDefault("preamble"))],
    queue: Annotated[str, typer.Option(default_factory=SubmitDefault("queue"))],
    split_every: Annotated[Time, typer.Option(parser=Time.parse, default_factory=SubmitDefault("split_every"))],
    start_after: Annotated[str, typer.Option(default_factory=SubmitDefault("start_after"))],
    walltime: Annotated[Time, typer.Option(parser=Time.parse, default_factory=SubmitDefault("walltime"))],
):
    """Submit a job to the queue."""
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
    """Sync the local directory with the remote directory on the HPC."""
    cli_config.check_ssh(msg=f"Sync requires a SSH configuration in '{CONFIG_FILENAME}'.")
    execute_sync()


if __name__ == "__main__":
    cli()
