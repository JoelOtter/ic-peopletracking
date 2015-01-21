ic-peopletracking
=================

Repository for 3rd year coursework

## Development

### Tracking

First, we need to install the track package.
`python setup.py develop` This will setup symlinks for the package, and allow changes to be made to the original.
`ic_track -v path_to_video --dump-json` Will return JSON data containing the location of the person in the video specified.
Running the same command with the `--display-video` flag will show the video with rectangles bordering the people detected.

### Shovel

This project includes a variety of opportunities to automate tasks, and the framework of choice
is shovel. This is a lightweight python library that is built around a single annotation, and
should be very easy to grasp.

To run any of the tasks in this project, first install shovel (`pip` should be the place to go)
and then run...

    shovel help

This will index all the shovel commands, with small descriptions of what the tasks do and how
to invoke them.

