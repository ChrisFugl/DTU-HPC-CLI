# DTU HPC CLI
CLI for working with the High Performance Cluster (HPC) at Technical University of Denmark (DTU). This CLI is a wrapper around the tools provided by the HPC to make it easier to run and manage jobs. See the [HPC documentation](https://www.hpc.dtu.dk) for more information.

## Requirements

The CLI assumes that you have access to the following shell commands:

* ssh

## Installation

The CLI can be installed using pip:

``` sh
pip install dtu-hpc-cli
```

## Configuration

You will need to configure the CLI for each project, such that it knows what to install and how to connect to the HPC. You do this by creating a `.dtu_hpc.json` in the root of your project. (We suggest that you add this file to .gitignore since the SSH configuration is specific to each user.)

``` json
{
    "install": [
        "pip install -r requirements.txt"
    ],
    "remote_path": "path/to/project/on/hpc",
    "ssh": {
        "user": "your_dtu_username",
        "identityfile": "/your/local/path/to/private/key"
    },
    "submit": {
        "branch": "main",
        "commands": [
            "python my_script.py"
        ],
        "cores": 4,
        "feature": [
            "gpu32gb"
        ],
        "error": "path/to/error_$J.err",
        "gpus": 1,
        "hosts": 1,
        "memory": "5GB",
        "model": "XeonGold6230",
        "name": "my_job",
        "output": "path/to/output_$J.out",
        "queue": "hpc",
        "split_every": "1d",
        "start_after": "12345678",
        "walltime": "1d"
    }
}
```

**remote_path** *(optional)*: Path to your project on HPC. Defaults to *~/[name]-[hash]* where *[name]* is the project directory name on your local machine and *[hash]* is generated based on the path to *[name]* on your local machine.

**ssh**: These keys are available: *host*, *user*, and *identityfile*. *host* is optional and defaults to *"login1.hpc.dtu.dk"`*.