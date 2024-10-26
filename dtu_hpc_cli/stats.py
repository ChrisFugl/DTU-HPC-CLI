import dataclasses

from dtu_hpc_cli.client import get_client


@dataclasses.dataclass
class StatsConfig:
    cpu: bool
    gpu: bool
    jobs: bool
    memory: bool
    node: str | None
    reserved: bool
    queue: str | None


def execute_stats(config: StatsConfig):
    command = ["nodestat"]

    if config.cpu:
        command.append("-f")

    if config.gpu:
        command.append("-G")

    if config.jobs:
        command.append("-J")

    if config.memory:
        command.append("-m")

    if config.node is not None:
        command.append("-n")
        command.append(config.node)

    if config.reserved:
        command.append("-r")

    if config.queue is not None:
        command.append(config.queue)

    command = " ".join(command)

    with get_client() as client:
        client.run(command)
