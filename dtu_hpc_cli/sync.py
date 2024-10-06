import subprocess

import typer
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn

from dtu_hpc_cli.config import Config


def execute_sync(cli_config: Config):
    ssh = cli_config.ssh
    source = "./"
    destination = f"{ssh.user}@{ssh.hostname}:{cli_config.remote_path}"
    command = [
        "rsync",
        "-avz",
        "-e",
        f"ssh -i {ssh.identityfile}",
        "--exclude-from=.gitignore",
        source,
        destination,
    ]

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task(description="Syncing", total=None)
        progress.start()
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            typer.echo(f"Sync failed: {e}")
            raise typer.Exit(code=1) from e
        progress.update(task, completed=True)
    typer.echo("Finished synchronizing")
