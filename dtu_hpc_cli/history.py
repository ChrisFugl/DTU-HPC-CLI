import json

from dtu_hpc_cli.config import SubmitConfig
from dtu_hpc_cli.config import cli_config


def add_to_history(submit_config: SubmitConfig, job_ids: list[str]):
    history = load_history()
    history.append({"config": submit_config.to_dict(), "job_ids": job_ids})
    save_history(history)


def load_history() -> list[dict]:
    path = cli_config.history_path
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save_history(history: list[dict]):
    path = cli_config.history_path
    path.write_text(json.dumps(history))
