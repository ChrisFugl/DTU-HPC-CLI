# TODO: configurable defaults for output and error locations

import dataclasses
from enum import StrEnum
from textwrap import dedent

import typer

from dtu_hpc_cli.client import Client
from dtu_hpc_cli.config import Config
from dtu_hpc_cli.types import Time


class Queue(StrEnum):
    gpuamd = "gpuamd"
    gpua10 = "gpua10"
    gpua40 = "gpua40"
    gpua100 = "gpua100"
    gpuv100 = "gpuv100"
    hpc = "hpc"


class Feature(StrEnum):
    avx = "avx"
    avx2 = "avx2"
    avx512 = "avx512"
    gpu16gb = "gpu16gb"
    gpu32gb = "gpu32gb"
    gpu40gb = "gpu40gb"
    gpu80gb = "gpu80gb"
    sm61 = "sm61"
    sm70 = "sm70"
    sm80 = "sm80"
    sm86 = "sm86"
    sm90 = "sm90"
    sxm2 = "sxm2"


class Model(StrEnum):
    EPYC7542 = "EPYC7542"
    EPYC7543 = "EPYC7543"
    EPYC7551 = "EPYC7551"
    EPYC9354 = "EPYC9354"
    EPYC9554 = "EPYC9554"
    XeonGold6126 = "XeonGold6126"
    XeonGold6142 = "XeonGold6142"
    XeonGold6226R = "XeonGold6226R"
    XeonGold6230 = "XeonGold6230"
    XeonGold6242 = "XeonGold6242"
    XeonGold6326 = "XeonGold6326"
    XeonGold6342 = "XeonGold6342"
    XeonE5_2609v4 = "XeonE5_2609v4"
    XeonE5_2650v4 = "XeonE5_2650v4"
    XeonE5_2660v3 = "XeonE5_2660v3"
    XeonPlatinum8462Y = "XeonPlatinum8462Y"
    XeonSilver4110 = "XeonSilver4110"


@dataclasses.dataclass
class SubmitConfig:
    branch: str
    commands: list[str]
    cores: int
    features: list[Feature] | None
    error: str | None
    gpus: int | None
    hosts: int
    model: Model | None
    output: str | None
    queue: Queue
    memory: int
    name: str
    split_every: Time
    walltime: Time
    start_after: str | None


def execute_submit(config: Config, submit_config: SubmitConfig):
    # with Client(config) as client:
    #     output = client.run("bstat")
    # print(output)

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
        submit_multiple(config, submit_config)
    else:
        submit_once(config, submit_config)


def submit_once(config: Config, submit_config: SubmitConfig):
    print("once")


def submit_multiple(config: Config, submit_config: SubmitConfig):
    counter = 1
    time_left = submit_config.walltime
    while not time_left.is_zero():
        job_name = f"{submit_config.name}-{counter}"
        job_walltime = time_left if time_left < submit_config.split_every else submit_config.split_every
        job_config = dataclasses.replace(submit_config, name=job_name, walltime=job_walltime)
        print(counter)
        counter += 1
        time_left -= job_walltime


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
