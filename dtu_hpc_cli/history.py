import dataclasses
import json
import time

import typer
from rich.console import Console
from rich.table import Table

from dtu_hpc_cli.config import SubmitConfig
from dtu_hpc_cli.config import cli_config


@dataclasses.dataclass
class HistoryConfig:
    branch: bool
    commands: bool
    cores: bool
    feature: bool
    error: bool
    gpus: bool
    hosts: bool
    limit: int
    memory: bool
    model: bool
    name: bool
    output: bool
    queue: bool
    preamble: bool
    split_every: bool
    start_after: bool
    walltime: bool


def execute_history(config: HistoryConfig):
    history = load_history()
    if len(history) == 0:
        typer.echo(f"No history found in '{cli_config.history_path}'. You might not have submitted any jobs yet.")
        return

    history.reverse()
    history = history[: config.limit] if config.limit > 0 else history

    table = Table(title="Job submissions", show_lines=True)
    table.add_column("job ID(s)")
    if config.name:
        table.add_column("name")
    if config.queue:
        table.add_column("queue")
    if config.cores:
        table.add_column("cores")
    if config.gpus:
        table.add_column("gpus")
    if config.hosts:
        table.add_column("hosts")
    if config.memory:
        table.add_column("memory")
    if config.model:
        table.add_column("model")
    if config.feature:
        table.add_column("feature(s)")
    if config.walltime:
        table.add_column("walltime")
    if config.output:
        table.add_column("output")
    if config.error:
        table.add_column("error")
    if config.split_every:
        table.add_column("split_every")
    if config.start_after:
        table.add_column("start_after")
    if config.branch:
        table.add_column("branch")
    if config.preamble:
        table.add_column("preamble")
    if config.commands:
        table.add_column("command(s)")

    for entry in history:
        values = SubmitConfig.from_dict(entry["config"])
        job_ids = entry["job_ids"]
        row = ["\n".join(job_ids)]
        if config.name:
            row.append(values.name)
        if config.queue:
            row.append(values.queue.value)
        if config.cores:
            row.append(str(values.cores))
        if config.gpus:
            row.append(str(values.gpus) if values.gpus is not None and values.gpus > 0 else "-")
        if config.hosts:
            row.append(str(values.hosts))
        if config.memory:
            row.append(str(values.memory))
        if config.model:
            row.append(values.model.value if values.model is not None else "-")
        if config.feature:
            row.append(
                "\n".join(feature.value for feature in values.feature)
                if values.feature is not None and len(values.feature) > 0
                else "-"
            )
        if config.walltime:
            row.append(str(values.walltime))
        if config.output:
            row.append(values.output if values.output is not None else "-")
        if config.error:
            row.append(values.error if values.error is not None else "-")
        if config.split_every:
            row.append(str(values.split_every))
        if config.start_after:
            row.append(values.start_after if values.start_after is not None else "-")
        if config.branch:
            row.append(values.branch if values.branch is not None else "-")
        if config.preamble:
            row.append("\n".join(values.preamble) if len(values.preamble) > 0 else "-")
        if config.commands:
            row.append("\n".join(values.commands))
        table.add_row(*row)

    console = Console()
    console.print(table)


def add_to_history(submit_config: SubmitConfig, job_ids: list[str]):
    history = load_history()
    history.append({"config": submit_config.to_dict(), "job_ids": job_ids, "timestamp": time.time()})
    save_history(history)


def load_history() -> list[dict]:
    path = cli_config.history_path
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save_history(history: list[dict]):
    path = cli_config.history_path
    path.write_text(json.dumps(history))
