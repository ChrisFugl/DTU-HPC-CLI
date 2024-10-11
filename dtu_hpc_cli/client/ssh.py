import time

import paramiko

from dtu_hpc_cli.client.base import Client
from dtu_hpc_cli.config import cli_config
from dtu_hpc_cli.constants import CONFIG_FILENAME


class SSHClient(Client):
    def __init__(self):
        super().__init__()

        cli_config.check_ssh(msg=f"Please provide a SSH configuration in '{CONFIG_FILENAME}'.")

        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(
            hostname=cli_config.ssh.hostname,
            username=cli_config.ssh.user,
            key_filename=cli_config.ssh.identityfile,
            allow_agent=False,
        )

        self.sftp = None
        self.shell = self.client.invoke_shell()

        # Empty the initial messages from the HPC.
        self.read()

        self.num_prompt_lines = self.get_num_prompt_lines()

    def close(self):
        sftp = getattr(self, "sftp", None)
        if sftp is not None:
            sftp.close()
        shell = getattr(self, "shell", None)
        if shell is not None:
            shell.close()
        client = getattr(self, "client", None)
        if client is not None:
            client.close()

    def run(self, command: str, cwd: str | None = None) -> str:
        if cwd is not None:
            command = f"cd {cwd} && {command}"
        self.shell.sendall(f"{command}\n")

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