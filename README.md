ic-peopletracking
=================

Repository for 3rd year coursework

### Tracking

First, we need to install the track package.
`python setup.py develop` This will setup symlinks for the package, and allow changes to be made to the original.
`vidtojson path_to_video` Will return JSON data containing the location of the person in the video specified.
The data can be output to a file instead using the -f flag:
`vidtojson path_to_video -f path_to_output_file`
