from pathlib import Path


def get_project_root() -> Path:
    """Assyme that .dtc_hpc.json exist in the project root and use that to get the project root."""
    root = Path("/")
    current_path = Path.cwd()
    while current_path != root:
        if (current_path / ".dtu_hpc.json").exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(
        "Could not find project root. Make sure that .dtu_hpc.json exists in the root of the project."
    )
