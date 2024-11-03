import rich

from dtu_hpc_cli.client import get_client
from dtu_hpc_cli.config import cli_config


def execute_run(arguments: list[str]):
    if len(arguments) == 0:
        rich.print("[bold red]No command provided.")
        return

    command = " ".join(arguments)
    with get_client() as client:
        client.run(command, cwd=cli_config.remote_path)
