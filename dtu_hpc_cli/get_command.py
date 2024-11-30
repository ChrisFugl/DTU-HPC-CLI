import typer

from dtu_hpc_cli.history import find_job


def execute_get_command(job_id: str):
    config = find_job(job_id)

    preamble = config.pop("preamble", [])
    submit_commands = config.pop("commands", [])

    command = ["dtu submit"]
    for key, value in config.items():
        if value is None or (isinstance(value, list) and len(value) == 0):
            continue
        key = key.replace("_", "-")
        if isinstance(value, bool):
            if value:
                command.append(f"--{key}")
            else:
                command.append(f"--no-{key}")
        else:
            command.append(f"--{key} {value}")

    command.extend(f'--preamble "{c}"' for c in preamble)
    command.extend(f'"{c}"' for c in submit_commands)
    command = " \\\n    ".join(command)

    typer.echo(command)
