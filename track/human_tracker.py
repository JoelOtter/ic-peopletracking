import cv2

from mosse import MOSSE
from helpers import *


class HumanTracker:

    def __init__(self, frame_gray, target_bound):

        """
        Parameters
        ----------
        frame_gray: opencv grayscale frame instance
        Initial frame that contains image of human target.

        target_bound: (x, y, width, height)
        The rectangle that should be selected as a human to track.
        """

        self.mosse = MOSSE(frame_gray, self.calculate_mosse_target(target_bound))
        self.bound = target_bound

    def calculate_mosse_target(self, target_bound):
        x, y, w, h = target_bound

        pad_w = int(0.2 * w)
        pad_h = int(0.1 * h)

        x1 = max(0, x - pad_w)
        x2 = x + w + pad_w
        y1 = max(0, y - pad_h)
        y2 = y + pad_h + int(0.5 * h)  # heuristic for selecting torso

        return (x1, y1, x2, y2)

    def update(self, frame_gray, available_bounds):

        """
        Parameters
        ----------
        frame_gray: opencv grayscale frame instance
        Frame to process for next update

        available_bounds: list of boundaries, [(x, y, w, h)]
        Ordered by size of boundary descending.
        A collection of boundaries from which to select the most appropriate
        dependent on current position of mosse.
        """

        self.mosse.update(frame_gray)
        for bound in available_bounds:
            if is_inside(self.mosse.position, bound):
                self.bound = bound
                return

    def error_score(self):
        return self.mosse.bad_count

    def draw_state(self, frame):
        x, y, w, h = self.bound
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255))

    @property
    def position(self):
        return self.mosse.position

