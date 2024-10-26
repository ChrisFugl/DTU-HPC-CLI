from dtu_hpc_cli.client import get_client


def execute_queues():
    with get_client() as client:
        client.run("bqueues")
