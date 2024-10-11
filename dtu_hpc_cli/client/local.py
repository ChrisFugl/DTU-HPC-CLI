import os
import subprocess

from dtu_hpc_cli.client.base import Client


class LocalClient(Client):
    def close(self):
        pass

    def run(self, command: str, cwd: str | None = None, ssh_timeout: float = 0.25) -> str:
        # Ignore the cwd parameter since we assume that the user is running the command from the correct directory.
        output = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return output.stdout

    def remove(self, path: str):
        os.remove(path)

    def save(self, path: str, contents: str):
        with open(path, "w") as f:
            f.write(contents)
