import dataclasses
import enum

from dtu_hpc_cli.client import get_client


class ListStats(enum.StrEnum):
    cpu = "cpu"
    memory = "memory"


@dataclasses.dataclass
class ListConfig:
    node: str | None
    queue: str | None
    stats: ListStats | None


def execute_list(list_config: ListConfig):
    command = ["bstat"]
    match list_config.stats:
        case ListStats.cpu:
            command.append("-C")
        case ListStats.memory:
            command.append("-M")

    if list_config.node is not None:
        command.extend(["-n", list_config.node])

    if list_config.queue is not None:
        command.extend(["-q", list_config.queue])

    command = " ".join(command)

    with get_client() as client:
        output = client.run(command)
    print(output)
