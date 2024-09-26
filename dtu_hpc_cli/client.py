# TODO: support running on HPC and SSH into the HPC
# TODO: capture stderr

import abc
import time

import paramiko

from dtu_hpc_cli.config import Config


class Client(abc.ABC):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    @abc.abstractmethod
    def run(self, command: str) -> str:
        pass

    @abc.abstractmethod
    def cd(self, path: str):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def remove(self, path: str):
        pass

    @abc.abstractmethod
    def save(self, path: str, contents: str):
        pass

    @abc.abstractmethod
    def is_local(self) -> bool:
        pass

    @abc.abstractmethod
    def is_remote(self) -> bool:
        pass


def get_client(config: Config) -> Client:
    # TODO: handle local and global case
    return SSHClient(config)


class SSHClient(Client):
    def __init__(self, config: Config):
        super().__init__()

        self.config = config

        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(
            hostname=self.config.ssh.credentials.hostname,
            username=self.config.ssh.credentials.user,
            key_filename=self.config.ssh.credentials.identityfile,
            allow_agent=False,
        )

        self.sftp = None
        self.shell = self.client.invoke_shell()

        # Empty the initial messages from the HPC.
        self.read()

        self.num_prompt_lines = self.get_num_prompt_lines()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        if self.sftp is not None:
            self.sftp.close()
            self.sftp = None
        self.shell.close()
        self.client.close()

    def cd(self, path: str):
        self.run(f"cd {path}")

    def is_local(self) -> bool:
        return False

    def is_remote(self) -> bool:
        return True

    def run(self, command: str):
        self.shell.send(f"{command}\n")

        output = self.read().strip()
        output = self.remove_prompt(output)

        start = len(command) + 2  # +2 for the \r\n
        output = output[start:]

        return output

    def remove(self, path: str):
        if self.sftp is None:
            self.sftp = self.client.open_sftp()
        self.sftp.remove(path)

    def save(self, path: str, contents: str):
        if self.sftp is None:
            self.sftp = self.client.open_sftp()
        with self.sftp.file(path, "w") as f:
            f.write(contents)

    def read(self, capacity: int = 1024, wait: float = 0.25) -> str:
        output: list[str] = []
        while True:
            if not self.shell.recv_ready():
                # Hack: HPC will print several messages, but they might not occur at the same time.
                # We wait for a short period to see if more messages are arriving.
                time.sleep(wait)
                if not self.shell.recv_ready():
                    break
            msg = self.shell.recv(capacity)
            msg = msg.decode("utf-8")
            output.append(msg)
        output = "".join(output)
        return output

    def get_num_prompt_lines(self) -> int:
        """Count number of lines used for the user prompt.

        We can get this by sending an echo command and counting the number of lines after the output.
        """
        msg = "foo"
        command = f"echo {msg}"
        self.shell.send(f"{command}\n")

        output = self.read().strip()
        lines = output.split("\r\n")
        index = 0
        for line in lines:
            if msg in line and command not in line:
                break
            index += 1
        return len(lines) - index - 1

    def remove_prompt(self, output: str) -> str:
        """The prompt is included in stdout, so we remove it."""
        lines = output.split("\r\n")
        return "\r\n".join(lines[: -self.num_prompt_lines])
