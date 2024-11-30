import dataclasses

from dtu_hpc_cli.config import Memory
from dtu_hpc_cli.config import SubmitConfig
from dtu_hpc_cli.config import Time
from dtu_hpc_cli.history import find_job
from dtu_hpc_cli.submit import execute_submit


@dataclasses.dataclass
class ResubmitConfig:
    job_id: str

    branch: str | None
    commands: list[str] | None
    cores: int | None
    feature: list[str] | None
    error: str | None
    gpus: int | None
    hosts: int | None
    memory: Memory | None
    model: str | None
    name: str | None
    output: str | None
    queue: str | None
    preamble: list[str]
    split_every: Time | None
    start_after: str | None
    sync: bool | None
    walltime: Time | None


def execute_resubmit(config: ResubmitConfig):
    submit_config = find_job(config.job_id)
    submit_config = SubmitConfig.from_dict(submit_config)

    replacements = {
        "branch": config.branch,
        "commands": config.commands,
        "cores": config.cores,
        "feature": config.feature,
        "error": config.error,
        "gpus": config.gpus,
        "hosts": config.hosts,
        "memory": config.memory,
        "model": config.model,
        "name": config.name,
        "output": config.output,
        "queue": config.queue,
        "preamble": config.preamble,
        "split_every": config.split_every,
        "start_after": config.start_after,
        "sync": config.sync,
        "walltime": config.walltime,
    }
    replacements = {key: value for key, value in replacements.items() if value is not None}

    submit_config = dataclasses.replace(submit_config, **replacements)

    execute_submit(submit_config)
