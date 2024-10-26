import dataclasses

from dtu_hpc_cli.client import get_client


@dataclasses.dataclass
class StartTimeConfig:
    job_ids: list[str] | None
    queue: str | None
    user: str | None


def execute_start_time(config: StartTimeConfig):
    command = ["showstart"]

    if config.queue is not None:
        command.append("-q")
        command.append(config.queue)

    if config.user is not None:
        command.append("-u")
        command.append(config.user)

    if config.job_ids is not None:
        command.extend(config.job_ids)

    command = " ".join(command)

    with get_client() as client:
        client.run(command)
