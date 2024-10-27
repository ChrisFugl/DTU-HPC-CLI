import rich

from dtu_hpc_cli.client import get_client
from dtu_hpc_cli.config import cli_config


def execute_run(commands: list[str]):
    with get_client() as client:
        for command in commands:
            rich.print(f"[bold blue]> {command}")
            client.run(command, cwd=cli_config.remote_path)
