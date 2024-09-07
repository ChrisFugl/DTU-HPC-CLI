import time

import paramiko

from dtu_hpc_cli.config import Config


class Client:
    def __init__(self, config: Config):
        self.config = config

        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(
            hostname=self.config.ssh.credentials.hostname,
            username=self.config.ssh.credentials.user,
            key_filename=self.config.ssh.credentials.identityfile,
            allow_agent=False,
        )

        self.shell = self.client.invoke_shell()

        # We read the initial messages from HPC to know what the user prompt looks like.
        self.init_messages = self.read().strip()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        self.shell.close()
        self.client.close()

    def run(self, command: str):
        self.shell.send(f"{command}\n")

        output = self.read().strip()
        output = self.remove_prompt(output)

        start = len(command) + 2  # +2 for the \r\n
        output = output[start:]

        return output

    def read(self, capacity: int = 1024, wait: float = 0.25) -> str:
        output: list[str] = []
        while True:
            if not self.shell.recv_ready():
                # Hack: HPC will print several messages, but they will not occur at the same time.
                # We wait for a short period to see if more messages are arriving.
                time.sleep(wait)
                if not self.shell.recv_ready():
                    break
            msg = self.shell.recv(capacity)
            msg = msg.decode("utf-8")
            output.append(msg)
        output = "".join(output)
        return output

    def remove_prompt(self, output: str) -> str:
        """The prompt is included in stdout, so we remove it."""
        init_index = len(self.init_messages) - 1
        output_end = len(output) - 1
        while init_index >= 0 and output_end >= 0 and self.init_messages[init_index] == output[output_end]:
            init_index -= 1
            output_end -= 1
        return output[: output_end + 1]
