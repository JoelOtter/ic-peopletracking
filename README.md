ic-peopletracking
=================

Repository for 3rd year coursework

## Development

### Shovel

This project includes a variety of opportunities to automate tasks, and the framework of choice
is shovel. This is a lightweight python library that is built around a single annotation, and
should be very easy to grasp.

To run any of the tasks in this project, first install shovel (`pip` should be the place to go)
and then run...

    shovel help

This will index all the shovel commands, with small descriptions of what the tasks do and how
to invoke them.

### Git Hooks

Hooks are used to enforce coding styles and to enable some development interactivity that should
improve productivity when working on ic-peopletracker.

To enable hooks, please run `shovel install.git_hooks` from the project root. Until then, the hooks
will not be active.

Currently, the following hooks are enabled...

`prepare-commit-msg`: used to append output from \*`ghi` to commit messages

`pre-commit`: runs code styling checks and prompts user to accept violations

\* `ghi` is a ruby gem to inspect github issues, and can be installed by running `gem install ghi`


