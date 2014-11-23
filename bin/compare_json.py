#!/usr/bin/env python
import track
import argparse
import re
import json


parser = argparse.ArgumentParser(
    description='Compare tracking data against expected test')

parser.add_argument('video',
                    metavar='./video.avi',
                    help='target video file'
                    )

parser.add_argument('expected',
                    metavar='./test.json',
                    help='expected json readings'
                    )


def run():

    args = parser.parse_args()

    generated_json = json.loads(track.JSON_from_video(args.video))
    expected_json = json.load(open(args.expected, 'r'))

    common_frames = match_common_frames(expected_json, generated_json)
    overlap_pcts = generate_frame_overlaps(common_frames)

    print """
    Overlap Percentages (pct of expected rectangle covered)
    =======================================================
    Average:    {average_overlap}%
    Minimum:    {minimum_overlap}%
    Maximum:    {maximum_overlap}%
    """.format(
        average_overlap=round((sum(overlap_pcts) / len(overlap_pcts)), 2),
        minimum_overlap=round((min(overlap_pcts)), 2),
        maximum_overlap=round((max(overlap_pcts)), 2)
    )


def match_common_frames(exp, gen):

    common_frames = {}

    for result in exp:
        common_frames[result['frame']] = {
            'exp': result['rectangles'][0]
        }

    for result in gen:
        frame_num = result['frame']
        if frame_num in common_frames:
            common_frames[frame_num]['gen'] = result['rectangles'][0]

    return {k: v for k, v in common_frames.items() if 'gen' in v}


def generate_frame_overlaps(frames):

    frame_overlap_pcts = []

    for (frame_num, frame) in frames.items():

        expRect = Rect.from_dict(frame['exp'])
        genRect = Rect.from_dict(frame['gen'])

        overlap_pct = 100 * expRect.intersection(genRect) / expRect.area()
        frame_overlap_pcts.append(overlap_pct)

    return frame_overlap_pcts


class Rect:

    @staticmethod
    def from_dict(rect):
        return Rect(rect['x'], rect['y'], rect['width'], rect['height'])

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h

    def intersection(self, rectInstance):

        rect = rectInstance.__dict__

        if ((self.x + self.w) < rect['x']) \
            or (self.x > (rect['x'] + rect['w'])) \
            or ((self.y + self.h) < rect['y']) \
                or (self.y > (rect['y'] + rect['h'])):
                return 0

        width = (min(self.x + self.w, rect['x'] + rect['w']) - max(self.x, rect['x']))
        height = (min(self.y + self.h, rect['y'] + rect['h']) - max(self.y, rect['y']))

        return width * height


run()

