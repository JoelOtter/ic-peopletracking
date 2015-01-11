import numpy as np
import cv2
from mosse import MOSSE
from human_tracker import HumanTracker


class Tracker:

    def __init__(self, video_src, tween=10, mosse_tolerance=10, paused=False, display=False):
        self.display = display
        self.paused = paused
        self.tween = tween
        self.mosse_tolerance = mosse_tolerance

        self.cap = cv2.VideoCapture(video_src)
        self.next_frame()

        self.trackers = []
        self.human_tracker = HumanTracker()

        if display: cv2.imshow('frame', self.frame)

    def next_frame(self):
        ret, self.frame = self.cap.read()
        if not ret: return None
        self.frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        return self.frame

    def analyse(self):
        while self.paused or self.next_frame() is not None:
            if not self.paused:
                self.analyse_frame()
                self.update_trackers()
            if self.display: self.draw_and_wait()

    def analyse_frame(self):
        for bound in self.human_tracker.get_human_bounds(
            self.frame,
            map(lambda tracker: tracker.position, self.trackers)
        ):
            self.add_tracker(bound)

    # Adds a new tracker with the given bound to the collection.
    def add_tracker(self, bound):
        bx, by, bw, bh = bound
        pad_w = int(0.2 * bw)
        pad_h = int(0.1 * bh)

        x1 = max(0, bx - pad_w)
        x2 = max(0, bx + bw + pad_w)
        y1 = max(0, by - pad_h)
        y2 = max(0, by + bh + pad_h)

        cv2.rectangle(self.frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

        tracker = MOSSE(self.frame_gray, (x1, y1, x2, y2))
        self.trackers.append(tracker)

    # Send new frame to all trackers, allowing position adjustments. If any
    # trackers have now exceeded limit on bad count, remove them from the
    # collection.
    def update_trackers(self):
        for tracker in self.trackers[:]:
            tracker.update(self.frame_gray)
            if tracker.bad_count > self.mosse_tolerance:
                self.trackers.remove(tracker)

    def draw_and_wait(self):

        # If the program is currently paused, then there is no need to redraw
        # any trackers as they will not have changed.
        if not self.paused:
            frame = self.frame.copy()
            for tracker in self.trackers:
                tracker.draw_state(frame)

            cv2.imshow('frame', frame)

        # Legacy display. Leaving in for quick reference if required in debug.
        """
        if len(self.trackers) > 0:
            cv2.imshow('tracker state', self.trackers[-1].state_vis)
        """

        key = cv2.waitKey(self.tween)

        if key == ord(' '):
            self.paused = not self.paused

        if key == ord('c'):
            self.trackers = []


