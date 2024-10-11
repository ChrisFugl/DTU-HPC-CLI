import dataclasses
import json
from enum import StrEnum
from hashlib import sha256
from pathlib import Path

from dtu_hpc_cli.constants import CONFIG_FILENAME
from dtu_hpc_cli.constants import HISTORY_FILENAME
from dtu_hpc_cli.error import error_and_exit
from dtu_hpc_cli.types import Memory
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
            error_and_exit(f"Invalid type for ssh option in config. Expected dictionary but got {type(ssh)}.")

        hostname = ssh.get("host", DEFAULT_HOSTNAME)

        if "user" not in ssh:
            error_and_exit('"user" not found in SSH config.')
        user = ssh["user"]

        if "identityfile" not in ssh:
            error_and_exit('"identityfile" not found in SSH config')
        identityfile = ssh["identityfile"]

        return cls(hostname=hostname, identityfile=identityfile, user=user)


@dataclasses.dataclass
class SubmitConfig:
    branch: str | None
    commands: list[str]
    cores: int
    feature: list[Feature] | None
    error: str | None
    gpus: int | None
    hosts: int
    memory: Memory
    model: Model | None
    name: str
    output: str | None
    queue: Queue
    preamble: list[str]
    split_every: Time
    start_after: str | None
    walltime: Time

    @classmethod
    def defaults(cls):
        return {
            "branch": "main",
            "commands": [],
            "cores": 4,
            "feature": None,
            "error": None,
            "gpus": None,
            "hosts": 1,
            "memory": "5GB",
            "model": None,
            "name": "NONAME",
            "output": None,
            "queue": "hpc",
            "preamble": [],
            "split_every": "1d",
            "start_after": None,
            "walltime": "1d",
        }

    @classmethod
    def load(cls, config: dict):
        if "submit" not in config:
            return cls.defaults()

        submit = config["submit"]

        if not isinstance(submit, dict):
            error_and_exit(f"Invalid type for submit option in config. Expected dictionary but got {type(submit)}.")

        submit = {key.replace("-", "_"): value for key, value in submit.items()}
        for key in submit.keys():
            if key not in cls.__annotations__:
                error_and_exit(f"Unknown option in submit config: {key}")

        output = {**cls.defaults(), **submit}

        return output

    def to_dict(self):
        return {
            "branch": self.branch,
            "commands": self.commands,
            "cores": self.cores,
            "feature": [feature.value for feature in self.feature] if self.feature is not None else None,
            "error": self.error,
            "gpus": self.gpus,
            "hosts": self.hosts,
            "memory": str(self.memory),
            "model": self.model.value if self.model is not None else None,
            "name": self.name,
            "output": self.output,
            "queue": self.queue.value,
            "preamble": self.preamble,
            "split_every": str(self.split_every),
            "start_after": self.start_after,
            "walltime": str(self.walltime),
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            branch=data["branch"],
            commands=data["commands"],
            cores=data["cores"],
            feature=[Feature(feature) for feature in data["feature"]] if data["feature"] is not None else None,
            error=data["error"],
            gpus=data["gpus"],
            hosts=data["hosts"],
            memory=Memory.parse(data["memory"]),
            model=Model(data["model"]) if data["model"] is not None else None,
            name=data["name"],
            output=data["output"],
            queue=Queue(data["queue"]),
            preamble=data["preamble"],
            split_every=Time.parse(data["split_every"]),
            start_after=data["start_after"],
            walltime=Time.parse(data["walltime"]),
        )


@dataclasses.dataclass
class CLIConfig:
    history_path: Path
    install: list[str] | None
    project_root: Path
    remote_path: str
    ssh: SSHConfig | None
    submit: SubmitConfig | None

    @classmethod
    def load(cls):
        project_root = cls.get_project_root()
        path = project_root / CONFIG_FILENAME

        try:
            config = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            error_and_exit(f"Error while parsing config file at '{path}':\n{e}")

        if not isinstance(config, dict):
            error_and_exit(f"Invalid type for config. Expected dictionary but got {type(config)}.")

        install = config.get("install")
        if install is not None and not isinstance(config["install"], list):
            error_and_exit(
                f"Invalid type for install option in config. Expected list but got {type(config['install'])}."
            )

        history_path = cls.load_history_path(config, project_root)

        remote_path = cls.load_remote_path(config, project_root)
        ssh = SSHConfig.load(config)

        submit = SubmitConfig.load(config)

        return cls(
            history_path=history_path,
            install=install,
            project_root=project_root,
            remote_path=remote_path,
            ssh=ssh,
            submit=submit,
        )

    @classmethod
    def get_project_root(cls) -> Path:
        """Assume that config file exist in the project root and use that to get the project root."""
        root = Path("/")
        current_path = Path.cwd()
        while current_path != root:
            if (current_path / CONFIG_FILENAME).exists():
                return current_path
            current_path = current_path.parent

        if (root / CONFIG_FILENAME).exists():
            return root

        error_and_exit(
            f"Could not find project root. Make sure that '{CONFIG_FILENAME}' exists in the root of the project."
        )

    @classmethod
    def load_history_path(cls, config: dict, project_root: Path) -> Path:
        if "history_path" in config:
            history_path = config["history_path"]
            if not isinstance(history_path, str):
                error_and_exit(
                    f"Invalid type for history_path option in config. Expected string but got {type(history_path)}."
                )
            return Path(history_path)
        return project_root / HISTORY_FILENAME

    @classmethod
    def load_remote_path(cls, config: dict, project_root: Path) -> str:
        if "remote_path" in config:
            return config["remote_path"]

        name = project_root.name
        hash = sha256(str(project_root).encode()).hexdigest()[:8]
        return f"~/{name}-{hash}"

    def check_ssh(self, msg: str = "SSH configuration is required for this command."):
        if self.ssh is None:
            error_and_exit(msg)


cli_config = CLIConfig.load()
