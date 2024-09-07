import dataclasses
import json
from pathlib import Path

DEFAULT_HOSTNAME = "login1.hpc.dtu.dk"


@dataclasses.dataclass
class Config:
    ssh: "SSH"

    @classmethod
    def load(cls):
        path = Path.cwd() / ".dtu_hpc.json"

        if not path.exists():
            raise FileNotFoundError(f"{path} does not exist")

        config = json.loads(path.read_text())

        ssh = SSH.load(config)

        return cls(ssh=ssh)


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
