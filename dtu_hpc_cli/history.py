import dataclasses
import json
import time

import typer
from rich.console import Console
from rich.table import Table

from dtu_hpc_cli.config import SubmitConfig
from dtu_hpc_cli.config import cli_config
from dtu_hpc_cli.error import error_and_exit
from dtu_hpc_cli.types import Memory
from dtu_hpc_cli.types import Time


@dataclasses.dataclass
class HistoryConfig:
    branch: bool
    branch_contains: str | None
    branch_is: str | None
    commands: bool
    command_contains: str | None
    command_is: str | None
    cores: bool
    cores_above: int | None
    cores_below: int | None
    cores_is: int | None
    feature: bool
    feature_contains: str | None
    feature_is: str | None
    error: bool
    error_contains: str | None
    error_is: str | None
    gpus: bool
    gpus_above: int | None
    gpus_below: int | None
    gpus_is: int | None
    hosts: bool
    hosts_above: int | None
    hosts_below: int | None
    hosts_is: int | None
    limit: int
    memory: bool
    memory_above: Memory | None
    memory_below: Memory | None
    memory_is: Memory | None
    model: bool
    model_contains: str | None
    model_is: str | None
    name: bool
    name_contains: str | None
    name_is: str | None
    output: bool
    output_contains: str | None
    output_is: str | None
    queue: bool
    queue_contains: str | None
    queue_is: str | None
    preamble: bool
    preamble_contains: str | None
    preamble_is: str | None
    split_every: bool
    split_every_above: Time | None
    split_every_below: Time | None
    split_every_is: Time | None
    start_after: bool
    start_after_contains: str | None
    start_after_is: str | None
    sync: bool
    walltime: bool
    walltime_above: Time | None
    walltime_below: Time | None
    walltime_is: Time | None


def execute_history(config: HistoryConfig):
    history = load_history()
    if len(history) == 0:
        typer.echo(f"No history found in '{cli_config.history_path}'. You might not have submitted any jobs yet.")
        return

    history = filter_by_string(history, "branch", config.branch_contains, config.branch_is)
    history = filter_by_list_string(history, "commands", config.command_contains, config.command_is)
    history = filter_by_comparable(history, "cores", config.cores_above, config.cores_below, config.cores_is)
    history = filter_by_list_string(history, "feature", config.feature_contains, config.feature_is)
    history = filter_by_string(history, "error", config.error_contains, config.error_is)
    history = filter_by_comparable(history, "gpus", config.gpus_above, config.gpus_below, config.gpus_is)
    history = filter_by_comparable(history, "hosts", config.hosts_above, config.hosts_below, config.hosts_is)
    history = filter_by_parsable_comparable(
        history, "memory", Memory.parse, config.memory_above, config.memory_below, config.memory_is
    )
    history = filter_by_string(history, "model", config.model_contains, config.model_is)
    history = filter_by_string(history, "name", config.name_contains, config.name_is)
    history = filter_by_string(history, "output", config.output_contains, config.output_is)
    history = filter_by_string(history, "queue", config.queue_contains, config.queue_is)
    history = filter_by_list_string(history, "preamble", config.preamble_contains, config.preamble_is)
    history = filter_by_parsable_comparable(
        history, "split_every", Time.parse, config.split_every_above, config.split_every_below, config.split_every_is
    )
    history = filter_by_string(history, "start_after", config.start_after_contains, config.start_after_is)
    history = filter_by_parsable_comparable(
        history, "walltime", Time.parse, config.walltime_above, config.walltime_below, config.walltime_is
    )

    if len(history) == 0:
        typer.echo("No history found with the given filters.")
        return

    history = history[-config.limit :] if config.limit > 0 else history

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
    if config.sync:
        table.add_column("sync")
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
            row.append(values.queue)
        if config.cores:
            row.append(str(values.cores))
        if config.gpus:
            row.append(str(values.gpus) if values.gpus is not None and values.gpus > 0 else "-")
        if config.hosts:
            row.append(str(values.hosts))
        if config.memory:
            row.append(str(values.memory))
        if config.model:
            row.append(values.model if values.model is not None else "-")
        if config.feature:
            row.append(
                "\n".join(feature for feature in values.feature)
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
        if config.sync:
            row.append("yes" if values.sync else "no")
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


def find_job(job_id: str) -> dict:
    history = load_history()
    for entry in history:
        if job_id in entry["job_ids"]:
            return entry["config"]
    error_and_exit(f"Job '{job_id}' not found in history.")


def filter_by_string(history: list[dict], key: str, contains: str | None, equals: str | None) -> list[dict]:
    if contains is not None:
        history = [entry for entry in history if entry["config"][key] is not None and contains in entry["config"][key]]
    if equals is not None:
        history = [entry for entry in history if entry["config"][key] is not None and entry["config"][key] == equals]
    return history


def filter_by_list_string(history: list[dict], key: str, contains: str | None, equals: str | None) -> list[dict]:
    if contains is not None:
        history = [
            entry
            for entry in history
            if entry["config"][key] is not None and any(contains in value for value in entry["config"][key])
        ]
    if equals is not None:
        history = [
            entry
            for entry in history
            if entry["config"][key] is not None and any(value == equals for value in entry["config"][key])
        ]
    return history


def filter_by_comparable(
    history: list[dict],
    key: str,
    above: int | None,
    below: int | None,
    equals: int | None,
) -> list[dict]:
    if above is not None:
        history = [entry for entry in history if entry["config"][key] is not None and entry["config"][key] > above]
    if below is not None:
        history = [entry for entry in history if entry["config"][key] is not None and entry["config"][key] < below]
    if equals is not None:
        history = [entry for entry in history if entry["config"][key] is not None and entry["config"][key] == equals]
    return history


def filter_by_parsable_comparable(
    history: list[dict],
    key: str,
    parser: callable,
    above: Time | Memory | None,
    below: Time | Memory | None,
    equals: Time | Memory | None,
) -> list[dict]:
    if above is not None:
        history = [
            entry for entry in history if entry["config"][key] is not None and parser(entry["config"][key]) > above
        ]
    if below is not None:
        history = [
            entry for entry in history if entry["config"][key] is not None and parser(entry["config"][key]) < below
        ]
    if equals is not None:
        history = [
            entry for entry in history if entry["config"][key] is not None and parser(entry["config"][key]) == equals
        ]
    return history
