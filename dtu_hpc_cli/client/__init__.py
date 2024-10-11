from dtu_hpc_cli.client.base import Client
from dtu_hpc_cli.client.ssh import SSHClient


def get_client() -> Client:
    return SSHClient()
