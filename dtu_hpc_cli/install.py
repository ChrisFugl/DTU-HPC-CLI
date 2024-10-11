import typer
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn

from dtu_hpc_cli.client import get_client
from dtu_hpc_cli.config import cli_config
from dtu_hpc_cli.constants import CONFIG_FILENAME


def execute_install():
    if cli_config.install is not None:
        outputs = []
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task(description="Installing", total=None)
            progress.start()
            with get_client() as client:
                for command in cli_config.install:
                    progress.update(task, description=command)
                    output = client.run(command, cwd=cli_config.remote_path, ssh_timeout=30.0)
                    outputs.append(f"> {command}\n{output}")
            progress.update(task, completed=True)
        outputs = "\n".join(outputs)
        typer.echo(f"Finished installation. Here are the outputs:\n{outputs}")
    else:
        typer.echo(f"There is nothing to install. Please set the install field in '{CONFIG_FILENAME}'.")
