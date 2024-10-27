import dataclasses
import enum

from dtu_hpc_cli.client import get_client


class JobsStats(enum.StrEnum):
    cpu = "cpu"
    memory = "memory"


@dataclasses.dataclass
class JobsConfig:
    node: str | None
    queue: str | None
    stats: JobsStats | None


def execute_jobs(config: JobsConfig):
    command = ["bstat"]
    match config.stats:
        case JobsStats.cpu:
            command.append("-C")
        case JobsStats.memory:
            command.append("-M")

    if config.node is not None:
        command.extend(["-n", config.node])

    if config.queue is not None:
        command.extend(["-q", config.queue])

    command = " ".join(command)

    with get_client() as client:
        client.run(command)
