from dtu_hpc_cli.client import Client
from dtu_hpc_cli.config import Config


def execute_list(config: Config):
    with Client(config) as client:
        output = client.run("bstat")
    print(output)
