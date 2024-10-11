import subprocess

from dtu_hpc_cli.client.base import Client
from dtu_hpc_cli.client.local import LocalClient
from dtu_hpc_cli.client.ssh import SSHClient


def get_client() -> Client:
    # We assume that only HPC has access to the bstat command and use this to determine if we are on the HPC.
    try:
        subprocess.check_output("bstat", shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return LocalClient()
    except subprocess.CalledProcessError:
        return SSHClient()
