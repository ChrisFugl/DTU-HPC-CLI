import subprocess

import typer
from git import Repo
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.prompt import Confirm

from dtu_hpc_cli.config import cli_config
from dtu_hpc_cli.error import error_and_exit


def execute_sync():
    with Repo(cli_config.project_root) as repo:
        if repo.is_dirty() or len(repo.untracked_files) != 0:
            prompt = (
                "You have uncommitted changes.\n"
                + "This may cause problems with switching branches.\n"
                + "Do you want to continue synchronizing?"
            )
            confirmed = Confirm.ask(prompt, show_default=True, default=True)
            if not confirmed:
                raise typer.Exit()

    ssh = cli_config.ssh
    source = "./"
    destination = f"{ssh.user}@{ssh.hostname}:{cli_config.remote_path}"
    command = [
        "rsync",
        "-avz",
        "-e",
        f"ssh -i {ssh.identityfile}",
        "--exclude-from=.gitignore",
        "--delete",
        source,
        destination,
    ]

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task(description="Syncing", total=None)
        progress.start()
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            error_and_exit(f"Sync failed:\n{e.stderr.decode()}")
        progress.update(task, completed=True)
