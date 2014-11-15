#!/usr/bin/env python
from .. import track
import argparse

parser = argparse.ArgumentParser(
    description='Get JSON string of the locations of a person in a video.')
parser.add_argument('-v', '--video',
                    required=True,
                    help='target video file'
                    )
parser.add_argument('-f', '--file',
                    help='target output file'
                    )

args = parser.parse_args()
track.JSON_from_video('../tests/videos/across/across.avi')
