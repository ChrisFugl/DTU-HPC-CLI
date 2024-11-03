import dataclasses

import typer

from dtu_hpc_cli.client import get_client
from dtu_hpc_cli.history import load_history


@dataclasses.dataclass
class RemoveConfig:
    from_history: bool
    job_ids: list[str]


def execute_remove(config: RemoveConfig):
    job_ids = expand_job_ids(config)
    with get_client() as client:
        for job_id in job_ids:
            client.run(f"bkill {job_id}")


def expand_job_ids(config: RemoveConfig) -> list[str]:
    if not config.from_history:
        return config.job_ids

    history = load_history()
    requested_ids = set(config.job_ids)

    job_ids = requested_ids.copy()
    for entry in history:
        entry_job_ids = set(entry["job_ids"])
        if not entry_job_ids.isdisjoint(requested_ids):
            job_ids.update(entry_job_ids)

    new_job_ids = job_ids - requested_ids
    job_ids = sorted(job_ids)
    if len(new_job_ids) != 0:
        typer.echo("The following jobs will be removed (because --from-history flag was used):")
        for job_id in job_ids:
            typer.echo(f" * {job_id}")
        typer.confirm("\nRemove these jobs (enter to remove)?", abort=True, default=True)

    return job_ids
