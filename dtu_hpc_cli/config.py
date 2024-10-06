import dataclasses
import json
from enum import StrEnum
from hashlib import sha256
from pathlib import Path

import typer

from dtu_hpc_cli.constants import CONFIG_FILENAME
from dtu_hpc_cli.paths import get_project_root
from dtu_hpc_cli.types import Time

DEFAULT_HOSTNAME = "login1.hpc.dtu.dk"

DEFAULT_SUBMIT_BRANCH = "main"


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
class SSHConfig:
    hostname: str
    user: str
    identityfile: str

    @classmethod
    def load(cls, config: dict):
        if "ssh" not in config:
            return None

        ssh = config["ssh"]

        if not isinstance(ssh, dict):
            raise TypeError(f"Invalid type for ssh option in config (expected dictionary): {type(ssh)}")

        hostname = ssh.get("host", DEFAULT_HOSTNAME)

        if "user" not in ssh:
            raise KeyError('"user" not found in config')
        user = ssh["user"]

        if "identityfile" not in ssh:
            raise KeyError('"identityfile" not found in config')
        identityfile = ssh["identityfile"]

        return cls(hostname=hostname, identityfile=identityfile, user=user)


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


@dataclasses.dataclass
class CLIConfig:
    install: list[str] | None
    project_root: Path
    remote_path: str
    ssh: SSHConfig | None
    submit: SubmitConfig | None

    @classmethod
    def load(cls):
        project_root = get_project_root()
        path = project_root / CONFIG_FILENAME

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

    def check_ssh(self, msg: str = "SSH configuration is required for this command."):
        if self.ssh is None:
            raise typer.BadParameter(msg)
