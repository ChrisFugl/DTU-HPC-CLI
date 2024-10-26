import typer

from dtu_hpc_cli.error import error_and_exit
from dtu_hpc_cli.history import load_history


def execute_get_command(job_id: str):
    config = find_job(job_id)

    preamble = config.pop("preamble", [])
    submit_commands = config.pop("commands", [])

    command = ["dtu submit"]
    for key, value in config.items():
        if value is None or (isinstance(value, list) and len(value) == 0):
            continue
        key = key.replace("_", "-")
        command.append(f"--{key} {value}")

    command.extend(f'"{c}"' for c in preamble)
    command.extend(f'"{c}"' for c in submit_commands)
    command = " \\\n    ".join(command)

    typer.echo(command)


def find_job(job_id: str) -> dict:
    history = load_history()
    for entry in history:
        if job_id in entry["job_ids"]:
            return entry["config"]
    error_and_exit(f"Job '{job_id}' not found in history.")
