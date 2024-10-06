from pathlib import Path

from dtu_hpc_cli.constants import CONFIG_FILENAME


def get_project_root() -> Path:
    """Assume that config file exist in the project root and use that to get the project root."""
    root = Path("/")
    current_path = Path.cwd()
    while current_path != root:
        if (current_path / CONFIG_FILENAME).exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(
        f"Could not find project root. Make sure that '{CONFIG_FILENAME}' exists in the root of the project."
    )
