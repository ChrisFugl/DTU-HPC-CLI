from dtu_hpc_cli.client import get_client
from dtu_hpc_cli.config import Config


def execute_list(config: Config):
    with get_client(config) as client:
        output = client.run("bstat")
    print(output)
