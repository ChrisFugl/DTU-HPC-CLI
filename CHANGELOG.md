# Changelogs

## v1.2.0

Option to show CLI version with `--version`.

Remove:
* Show default option in prompt when using `--from-history`.

Run:
* Run a single command instead of potentially multiple.
* All arguments are passed on to the remote command. E.g. `dtu run "ls -a"` is now `dtu run ls -a`.

Sync:
* Delete files remotely if they have been removed locally.

## v1.1.0

New commands:
* get-command
* queues
* run
* start-time
* stats

History:
* History list is no longer reversed, such that newest entries appear at the bottom.
* Added options to filter the history.
* Limit defaults to 5.

List:
* Renamed to *jobs* to better comply with the other *list* commands (*history* and *queues*).

Remove:
* Added `--from-history` option. This will search the history and add any extra job IDs associated with the submissions of a job (due to splitting).

Bug fixes and enhancements:
* SSH connections would only allow for a maximum duration of 30 seconds for a command to finish.
* `--feature`, `--model` and `--queue` will now accept any string value. Was previously restricted to known enumerations, but we removed this because we cannot know these at all times.
* All commands have short descriptions (enter `dtu --help` to see them).