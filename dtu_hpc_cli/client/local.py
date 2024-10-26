import os
import subprocess

import typer

from dtu_hpc_cli.client.base import Client


class LocalClient(Client):
    def close(self):
        pass

    def run(self, command: str, cwd: str | None = None) -> tuple[int, str]:
        # Ignore the cwd parameter since we assume that the user is running the command from the correct directory.
        outputs = []
        with subprocess.Popen(
            command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        ) as process:
            for line in process.stdout:
                typer.echo(line, nl=False)
                outputs.append(line)
            returncode = process.wait()
        output = "".join(outputs)
        return returncode, output

    def remove(self, path: str):
        os.remove(path)

    def save(self, path: str, contents: str):
        with open(path, "w") as f:
            f.write(contents)
