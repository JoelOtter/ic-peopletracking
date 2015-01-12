import numpy as np
import cv2

from helpers import remove_bounds_containing
from mosse import MOSSE
from human_tracker import HumanTracker
from contour_detector import ContourDetector
from hog_detector import HOGDetector


class Tracker:

    def __init__(self, video_src, tween=10, mosse_tolerance=10, paused=False, display=False):
        self.display = display
        self.paused = paused
        self.tween = tween
        self.mosse_tolerance = mosse_tolerance

        self.trackers = []
        self.contours = ContourDetector(2)
        self.hog = HOGDetector()

        self.cap = cv2.VideoCapture(video_src)
        self.next_frame()

        if display: cv2.imshow('frame', self.frame)

    def next_frame(self):
        ret, frame = self.cap.read()
        if not ret: return None

        self.frame = cv2.resize(frame, (853, 480))

        self.available_bounds = self.contours.get_distinct_contour_bounds(self.frame)
        self.available_bounds.sort(key=lambda b: b[2] * b[3], reverse=True)

        self.frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        return self.frame

    def analyse(self):
        while self.paused or self.next_frame() is not None:
            if not self.paused:
                self.analyse_frame()
                self.update_trackers()
            if self.display: self.draw_and_wait()

    def analyse_frame(self):
        bounds_not_currently_tracked = remove_bounds_containing(
            self.available_bounds,
            map(lambda tracker: tracker.position, self.trackers)
        )

        for bound in self.hog.select_human_bounds(self.frame, bounds_not_currently_tracked):
            tracker = HumanTracker(self.frame_gray, bound)
            self.trackers.append(tracker)

    # Send new frame to all trackers, allowing position adjustments. If any
    # trackers have now exceeded limit on bad count, remove them from the
    # collection.
    def update_trackers(self):
        for tracker in self.trackers[:]:
            tracker.update(self.frame_gray, self.available_bounds)
            if tracker.error_score() > self.mosse_tolerance:
                self.trackers.remove(tracker)

    def draw_and_wait(self):

        # If the program is currently paused, then there is no need to redraw
        # any trackers as they will not have changed.
        if not self.paused:
            frame = self.frame.copy()
            for tracker in self.trackers:
                tracker.draw_state(frame)

            cv2.imshow('frame', frame)

        key = cv2.waitKey(self.tween)

        if key == ord(' '):
            self.paused = not self.paused

        if key == ord('c'):
            self.trackers = []

    def draw_contours(self, frame):
        for bound in self.available_bounds:
            x, y, w, h = bound
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0))


