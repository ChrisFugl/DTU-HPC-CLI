import dataclasses

from dtu_hpc_cli.config import Feature
from dtu_hpc_cli.config import Memory
from dtu_hpc_cli.config import Model
from dtu_hpc_cli.config import Queue
from dtu_hpc_cli.config import SubmitConfig
from dtu_hpc_cli.config import Time
from dtu_hpc_cli.error import error_and_exit
from dtu_hpc_cli.history import load_history
from dtu_hpc_cli.submit import execute_submit


@dataclasses.dataclass
class ResubmitConfig:
    job_id: str

    branch: str | None
    commands: list[str] | None
    cores: int | None
    feature: list[Feature] | None
    error: str | None
    gpus: int | None
    hosts: int | None
    memory: Memory | None
    model: Model | None
    name: str | None
    output: str | None
    queue: Queue | None
    preamble: list[str]
    split_every: Time | None
    start_after: str | None
    walltime: Time | None


def execute_resubmit(config: ResubmitConfig):
    submit_config = find_job(config.job_id)

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
        "walltime": config.walltime,
    }
    replacements = {key: value for key, value in replacements.items() if value is not None}

    submit_config = dataclasses.replace(submit_config, **replacements)

    execute_submit(submit_config)


def find_job(job_id: str) -> SubmitConfig:
    history = load_history()
    for entry in history:
        if job_id in entry["job_ids"]:
            return SubmitConfig.from_dict(entry["config"])
    error_and_exit(f"Job '{job_id}' not found in history.")
