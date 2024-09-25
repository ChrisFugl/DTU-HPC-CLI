from dtu_hpc_cli.client import get_client
from dtu_hpc_cli.config import Config


def execute_run(config: Config, commands: list[str]):
    # TODO: run on interactive node/gpu
    # TODO: sync

    with get_client(config) as client:
        for command in commands:
            output = client.run(command)
            print(output)
