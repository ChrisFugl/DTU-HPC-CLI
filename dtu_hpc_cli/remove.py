import typer

from dtu_hpc_cli.client import get_client


def execute_remove(job_ids: list[str]):
    with get_client() as client:
        for job_id in job_ids:
            output = client.run(f"bkill {job_id}")
            typer.echo(output)
