# TODO: make SSH config optional and add method to check (and raise exception) if it is present
#   - use this method in commands that need SSH

# TODO: make name of config file a constant and search/replace in code

import dataclasses
import json
from hashlib import sha256
from pathlib import Path

from dtu_hpc_cli.paths import get_project_root

DEFAULT_HOSTNAME = "login1.hpc.dtu.dk"


@dataclasses.dataclass
class Config:
    install: list[str] | None
    project_root: Path
    remote_path: str
    ssh: "SSH"

    @classmethod
    def load(cls):
        project_root = get_project_root()
        path = project_root / ".dtu_hpc.json"

        if not path.exists():
            raise FileNotFoundError(f"{path} does not exist")

        config = json.loads(path.read_text())

        if not isinstance(config, dict):
            raise TypeError(f"Invalid type for config (expected dictionary): {type(config)}")

        install = config.get("install")
        if install is not None and not isinstance(config["install"], list):
            raise TypeError(f"Invalid type for install option in config (expected list): {type(config['install'])}")

        remote_path = cls.load_remote_path(config, project_root)
        ssh = SSH.load(config)

        return cls(install=install, project_root=project_root, remote_path=remote_path, ssh=ssh)

    def load_remote_path(config: dict, project_root: Path) -> str:
        if "remote_path" in config:
            return config["remote_path"]

        name = project_root.name
        hash = sha256(str(project_root).encode()).hexdigest()[:8]
        return f"~/{name}-{hash}"


@dataclasses.dataclass
class SSH:
    hostname: str
    user: str
    identityfile: str

    @classmethod
    def load(cls, config: dict):
        if "ssh" not in config:
            raise KeyError('"ssh" not found in config')

        ssh = config["ssh"]

        hostname = ssh.get("host", DEFAULT_HOSTNAME)

        if "user" not in ssh:
            raise KeyError('"user" not found in config')
        user = ssh["user"]

        if "identityfile" not in ssh:
            raise KeyError('"identityfile" not found in config')
        identityfile = ssh["identityfile"]

        return cls(hostname=hostname, identityfile=identityfile, user=user)
