#!/usr/bin/env python
import argparse
from track.track import Tracker


def check_video(file):
    if not file.endswith('.avi') and not file.endswith('.mp4'):
        raise argparse.ArgumentTypeError("Expected .avi or .mp4 video file")
    return file

parser = argparse.ArgumentParser(
    description='Runs tracking analysis of humans in the given video')

parser.add_argument('video', type=check_video)
parser.add_argument('--display-video',
                    help='displays a graphical display of tracking',
                    action='store_true')
parser.add_argument('--paused',
                    help='start the display paused',
                    action='store_true')

args = parser.parse_args()

print args
tracker = Tracker(
    args.video,
    display=bool(args.display_video),
    paused=bool(args.display_video) & bool(args.paused)
)

tracker.analyse()

