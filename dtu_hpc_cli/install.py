import typer
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn

from dtu_hpc_cli.client import get_client
from dtu_hpc_cli.config import cli_config
from dtu_hpc_cli.constants import CONFIG_FILENAME


def execute_install():
    if cli_config.install is not None:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task(description="Installing", total=None)
            progress.start()
            with get_client() as client:
                for command in cli_config.install:
                    progress.update(task, description=command)
                    client.run(command, cwd=cli_config.remote_path)
            progress.update(task, completed=True)
        typer.echo("Finished installation.")
    else:
        typer.echo(f"There is nothing to install. Please set the install field in '{CONFIG_FILENAME}'.")
