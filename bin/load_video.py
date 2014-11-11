#!/usr/bin/env python
import cv2
import argparse

BREAK_KEY = 27  # Escape key

parser = argparse.ArgumentParser(description='Display video frame by frame')
parser.add_argument('-v', '--video',
                    required=True,
                    metavar='./video.avi',
                    help='target video file'
                    )


def run():

    args = parser.parse_args()

    video_capture = load_video_capture(args.video)
    display_frames(video_capture)

    # Close video and clean up
    video_capture.release()
    cv2.destroyAllWindows()


def load_video_capture(video_file):
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        raise IOError("Failed to load video file")
    return cap


def display_frames(video_capture):

    wait_per_frame = int(1000/get_fps(video_capture))

    # Loop through each frame.
    for i in xrange(get_num_frames(video_capture)):

        ret, frame = video_capture.read()
        cv2.imshow('frame', frame)
        key = cv2.waitKey(wait_per_frame) & 0xff

        if key == BREAK_KEY:
            return


def get_num_frames(video_capture):
    return int(video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))


def get_fps(video_capture):
    return int(video_capture.get(cv2.cv.CV_CAP_PROP_FPS))

run()
