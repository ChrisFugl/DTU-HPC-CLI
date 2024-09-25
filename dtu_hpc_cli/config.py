import dataclasses
import json
from hashlib import sha256
from pathlib import Path

from dtu_hpc_cli.paths import get_project_root

DEFAULT_HOSTNAME = "login1.hpc.dtu.dk"


@dataclasses.dataclass
class Config:
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

        remote_path = cls.load_remote_path(config, project_root)
        ssh = SSH.load(config)

        return cls(project_root=project_root, remote_path=remote_path, ssh=ssh)

    def load_remote_path(config: dict, project_root: Path) -> str:
        if "remote_path" in config:
            return config["remote_path"]

        name = project_root.name
        hash = sha256(str(project_root).encode()).hexdigest()[:8]
        return f"~/{name}-{hash}"


@dataclasses.dataclass
class SSH:
    identifier: str | None = None
    credentials: "SSHCredentials" = None

    @classmethod
    def load(cls, config: dict):
        if "ssh" not in config:
            raise KeyError('"ssh" not found in config')

        ssh = config["ssh"]

        if isinstance(ssh, str):
            return cls(identifier=ssh)
        elif isinstance(ssh, dict):
            hostname = ssh.get("host", DEFAULT_HOSTNAME)

            if "user" not in ssh:
                raise KeyError('"user" not found in config')
            user = ssh["user"]

            if "identityfile" not in ssh:
                raise KeyError('"identityfile" not found in config')
            identityfile = ssh["identityfile"]

            return cls(credentials=SSHCredentials(hostname, user, identityfile))
        else:
            raise TypeError(f"Invalid type for ssh: {type(ssh)}")


@dataclasses.dataclass
class SSHCredentials:
    hostname: str
    user: str
    identityfile: str
