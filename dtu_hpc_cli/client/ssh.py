import fabric

from dtu_hpc_cli.client.base import Client
from dtu_hpc_cli.config import cli_config
from dtu_hpc_cli.constants import CONFIG_FILENAME


class SSHClient(Client):
    def __init__(self):
        super().__init__()

        cli_config.check_ssh(msg=f"Please provide a SSH configuration in '{CONFIG_FILENAME}'.")

        self.client = fabric.Connection(
            host=cli_config.ssh.hostname,
            user=cli_config.ssh.user,
            connect_kwargs={"key_filename": cli_config.ssh.identityfile},
        )

    def close(self):
        self.client.close()

    def run(self, command: str, cwd: str | None = None) -> tuple[int, str]:
        command = f'bash -l -c "{command}"'
        if cwd is not None:
            with self.client.cd(cwd):
                result = self.client.run(command, warn=True)
        else:
            result = self.client.run(command, warn=True)
        return result.exited, result.stdout

    def remove(self, path: str):
        sftp = self.client.sftp()
        sftp.remove(path)

    def save(self, path: str, contents: str):
        sftp = self.client.sftp()
        with sftp.file(path, "w") as f:
            f.write(contents)
