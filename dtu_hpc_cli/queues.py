from dtu_hpc_cli.client import get_client


def execute_queues(queue: str | None):
    if queue is None:
        command = "bqueues"
    else:
        command = f"classstat {queue}"

    with get_client() as client:
        client.run(command)
