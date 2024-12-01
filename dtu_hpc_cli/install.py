import typer
from git import Repo
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn

from dtu_hpc_cli.client import get_client
from dtu_hpc_cli.config import cli_config
from dtu_hpc_cli.constants import CONFIG_FILENAME
from dtu_hpc_cli.sync import execute_sync


def execute_install():
    install = cli_config.install
    if install is not None:
        if install.sync:
            execute_sync()
        with Repo(cli_config.project_root) as repo:
            branch = repo.active_branch.name
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task(description="Installing", total=None)
            progress.start()
            with get_client() as client:
                for command in install.commands:
                    command = f"git switch {branch} && {command}"
                    progress.update(task, description=command)
                    client.run(command, cwd=cli_config.remote_path)
            progress.update(task, completed=True)
        typer.echo("Finished installation.")
    else:
        typer.echo(f"There is nothing to install. Please set the install field in '{CONFIG_FILENAME}'.")
