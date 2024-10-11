# DTU HPC CLI
CLI for working with the High Performance Cluster (HPC) at the Technical University of Denmark (DTU). This CLI is a wrapper around the tools provided by the HPC to make it easier to run and manage jobs. See the [HPC documentation](https://www.hpc.dtu.dk) for more information.

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Example](#example)
5. [Configuration](#configuration)
    
    a. [SSH](#ssh)
    
    b. [Install](#install)

    c. [History](#history)

    d. [Remote Location](#remote-location)

    e. [Submit](#submit)

    f. [Complete Configuration](#complete-configuration)

## Requirements

Python v3.10+ is a requirement.

You will also need to have `rsync` installed for the `dtu sync` command` to work.

## Installation

The CLI can be installed using pip:

``` sh
pip install dtu-hpc-cli
```

You will also need to create a configuration in your project. See [Configuration](#configuration).

## Usage

You can call it using the `dtu` command, which has the these subcommands:

* **history**: Shows a list of the jobs that you have submitted and the options/commands that you used.
* **install**: Calls the installation commands in your configuration. NB. this command will install your project on the HPC - not on your local machine.
* **list**: Shows a list of running and pending jobs. It calls `bstat` on the HPC.
* **remove**: Removes (kills) one or more running or pending jobs. It calls `bkill` on the HPC.
* **resubmit**: Submits a job with the same options/commands as a previous job. Each option/command can optionally be overriden.
* **submit**: Submits a job to the HPC. Calls `bsub` on the HPC. NB. This command will automatically split a job into multiple jobs that run after each other when the walltime exceeds 24 hours. This is done because HPC limits GPU jobs to this duration. You can use the `--split-every` option to change duration at which jobs should be split.
* **sync**: Synchronizes your local project with the project on the HPC. Requires that you have the `rsync` command. NB. It ignores everything in `.gitignore`.

All commands will work out of the box on the HPC (except for `sync`). However, a big advantage of this tool is that you can call it from your local machine as well. You will need to [configure SSH](#ssh) for this to work.

## Example

A typical workflow will look like this:

1. Synchronize your local project with the HPC.

    ``` txt
    > dtu sync

    ⠹ Syncing
    Finished synchronizing
    ````

2. Install the project on the HPC. (Install commands are `["poetry install --sync"]` in this example.)

    ``` txt
    > dtu install

    ⠇ Installing
    Finished installation. Here are the outputs:
    > poetry install --sync
    Installing dependencies from lock file

    Package operations: 0 installs, 0 updates, 1 removal

    - Removing setuptools (69.5.1)
    ````

3. Submit a job. Use `dtu submit --help` to see all available options.

    ``` txt
    > dtu submit --name test --cores 2 --memory 2gb --walltime 1h "echo foo" "echo bar"

    Job script:

    #!/bin/sh
    ### General options
    #BSUB -J test
    #BSUB -q hpc
    #BSUB -n 2
    #BSUB -R rusage[mem=2GB]
    #BSUB -R span[hosts=1]
    #BSUB -W 01:00
    # -- end of LSF options --

    # Commands
    git switch main && echo foo
    git switch main && echo bar

    Submit job (enter to submit)? [Y/n]: y
    Submitting job...
    Submitted job <22862148>
    ```

4. Check that job is queued.

    ``` txt
    > dtu list

    JOBID      USER    QUEUE      JOB_NAME   NALLOC STAT  START_TIME      ELAPSED
    22862150   [user]  hpc        test            0 PEND       -          0:00:00
    ```

## Configuration

You will need to configure the CLI for each project, such that it knows what to install and how to connect to the HPC. You do this by creating `.dtu_hpc.json` in the root of your project. (We suggest that you add this file to .gitignore since the SSH configuration is specific to each user.)

All options in the configuration are optional, which means it can be as simple as this:

``` json
{}
```

However, we highly recommend to at least configure SSH to be able to manage jobs from your local machine.

See all options in [the complete example at the end](#complete-configuration).

### SSH

The SSH configuration requires that you at least add a *user* and *identityfile*. You may also optionally specify a hostname - it defaults to *login1.hpc.dtu.dk* when omitted.

``` json
{
    "ssh": {
        "user": "your_dtu_username",
        "identityfile": "/your/local/path/to/private/key"
    }
}
```

### Install

The `install` command requires that you provide a set of commands to run. These are provided using the *install* option.

``` json
{
    "install": [
        "pip install -r requirements.txt"
    ]
}
```

### History

The history of job submissions defaults to be saved to *.dtu_hpc_history.json* in the root of your project. You can override this location using *history_path*:

``` json
{
    "history_path": "path/to/history.json"
}
```

### Remote Location

The tool needs to know the location of your project on the HPC. The location defaults to *~/[name]-[hash]* where *[name]* is the project directory name on your local machine and *[hash]* is generated based on the path to *[name]* on your local machine. You can override this using *remote_path*:

``` json
{
    "remote_path": "path/to/project/on/hpc"
}
```

### Submit
The submit command has many options and you may want to provide sensible defaults for your specific application. Call `dtu submit --help` to see the existing defaults.

Any of the options can be given a custom default. As such, both of these are valid configurations for *submit*.

Only override a single option to use the V100 GPU queue as the default queue:

``` json
{
    "submit": {
        "queue": "gpuv100"
    }
}
```

Provide your own default settings for all *submit* options:

``` json
{
    "submit": {
        "branch": "main",
        "commands": [
            "python my_script.py"
        ],
        "cores": 4,
        "feature": [
            "gpu32gb"
        ],
        "error": "path/to/error_dir",
        "gpus": 1,
        "hosts": 1,
        "memory": "5GB",
        "model": "XeonGold6230",
        "name": "my_job",
        "output": "path/to/output_dir_",
        "queue": "hpc",
        "split_every": "1d",
        "start_after": "12345678",
        "walltime": "1d"
    }
}
```

**NB.** *error* and *output* are directory locations on the HPC. The file path will be `[directory]/[name]_[jobId].out` for output and `[directory]/[name]_[jobId].err` for error.

### Complete Configuration

Here is a complete example for a configuration that customizes everything:

``` json
{
    "history_path": "path/to/history.json",
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
        "error": "path/to/error_dir",
        "gpus": 1,
        "hosts": 1,
        "memory": "5GB",
        "model": "XeonGold6230",
        "name": "my_job",
        "output": "path/to/output_dir_",
        "queue": "hpc",
        "split_every": "1d",
        "start_after": "12345678",
        "walltime": "1d"
    }
}
```