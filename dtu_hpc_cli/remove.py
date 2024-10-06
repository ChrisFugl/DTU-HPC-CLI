import typer

from dtu_hpc_cli.client import get_client
from dtu_hpc_cli.config import Config


def execute_remove(cli_config: Config, job_ids: list[str]):
    with get_client(cli_config) as client:
        for job_id in job_ids:
            output = client.run(f"bkill {job_id}")
            typer.echo(output)
