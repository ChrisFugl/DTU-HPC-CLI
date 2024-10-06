# TODO: configurable defaults for output and error locations
# TODO: option to specify job preamble in submit command and in config file (the former overwrites the latter)
# TODO: log job submission to a history file

import dataclasses
import re
from textwrap import dedent
from uuid import uuid4

import typer

from dtu_hpc_cli.client import Client
from dtu_hpc_cli.client import get_client
from dtu_hpc_cli.config import CLIConfig
from dtu_hpc_cli.config import SubmitConfig

JOB_ID_PATTERN = re.compile(r"Job <([\d]+)> is submitted to queue")


def execute_submit(cli_config: CLIConfig, submit_config: SubmitConfig):
    if submit_config.walltime > submit_config.split_every:
        typer.echo(
            f"NB. This will result in multiple jobs as the split time is '{submit_config.split_every}' "
            + f"and the walltime '{submit_config.walltime}' exceeds that limit."
        )

    script = create_job_script(submit_config)
    typer.echo("Job script:")
    typer.echo(f"\n{script}\n")
    typer.confirm("Submit job (enter to submit)?", default=True, abort=True)

    typer.echo("Submitting job...")

    if submit_config.walltime > submit_config.split_every:
        submit_multiple(cli_config, submit_config)
    else:
        submit_once(cli_config, submit_config)


def submit_once(cli_config: CLIConfig, submit_config: SubmitConfig):
    with get_client(cli_config) as client:
        job_id = submit(client, cli_config, submit_config)
    print_submit_message(job_id, submit_config.start_after)


def submit_multiple(cli_config: CLIConfig, submit_config: SubmitConfig):
    with get_client(cli_config) as client:
        start_after = submit_config.start_after
        job_counter = 1
        time_left = submit_config.walltime
        while not time_left.is_zero():
            job_name = f"{submit_config.name}-{job_counter}"
            job_walltime = time_left if time_left < submit_config.split_every else submit_config.split_every
            job_config = dataclasses.replace(
                submit_config, name=job_name, start_after=start_after, walltime=job_walltime
            )
            job_id = submit(client, cli_config, job_config)
            print_submit_message(job_id, start_after)
            start_after = job_id
            job_counter += 1
            time_left -= job_walltime


def submit(client: Client, cli_config: CLIConfig, submit_config: SubmitConfig) -> str:
    job_script = create_job_script(submit_config)
    path = f"/tmp/{uuid4()}.sh"
    client.save(path, job_script)
    if client.is_remote():
        client.cd(cli_config.remote_path)
    stdout = client.run(f"bsub < {path}")
    client.remove(path)

    job_ids = JOB_ID_PATTERN.findall(stdout)
    if len(job_ids) != 1:
        raise Exception(f"Expected a single job ID from submitted job, but multiple from stdout:\n{stdout}")
    job_id = job_ids[0]
    return job_id


def create_job_script(config: SubmitConfig) -> str:
    augmented_commands = []
    for command in config.commands:
        augmented_command = command.strip()
        augmented_command = f"git switch {config.branch} && {augmented_command}"
        augmented_commands.append(augmented_command)
    augmented_commands = "\n    ".join(augmented_commands)

    options = [
        ("J", config.name),
        ("q", config.queue.value),
        ("n", config.cores),
        ("R", f"rusage[mem={config.memory}]"),
        ("R", f"span[hosts={config.hosts}]"),
        ("W", f"{config.walltime.total_hours():02d}:{config.walltime.minutes:02d}"),
    ]

    if config.gpus is not None:
        options.append(("gpu", f"num={config.gpus}:mode=exclusive_process"))

    if config.start_after is not None:
        options.append(("w", f"ended({config.start_after})"))

    if config.error is not None:
        options.append(("e", config.error))

    if config.output is not None:
        options.append(("o", config.output))

    if config.model is not None:
        options.append(("R", f'"select[model == X{config.model.value}]"'))

    features = [] if config.features is None else config.features
    for feature in features:
        options.append(("R", f'"select[{feature.value}]"'))

    options = "\n".join(f"    #BSUB -{flag} {value}" for flag, value in options)

    script = dedent(
        f"""
    #!/bin/sh
    ### General options\n{options}
    # -- end of LSF options --
    
    {augmented_commands}
    """
    )

    script = script.strip()

    return script


def print_submit_message(job_id: str, dependency: str | None):
    if dependency is None:
        typer.echo(f"Submitted job <{job_id}>")
    else:
        typer.echo(f"Submitted job <{job_id}> after <{dependency}>")
