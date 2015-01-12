import cv2
from helpers import *


class ContourDetector:

    def __init__(self, height_width_ratio=0, min_size=0, learning_rate=0.005):

        """
        Parameters
        ----------
        learning_rate: float, optional
        Rate at which background changes are assimilated into the background
        average.

        min_size: int, optional
        Minimum height/width of any contour bound.

        height_width_ratio: float, optional
        If this is set to N, then will discount all bounds that do not satisfy
        height > N * width.
        """

        self.learning_rate = learning_rate
        self.min_size = min_size
        self.height_width_ratio = height_width_ratio

        (
            self
            .init_bg_sub()
        )

    def init_bg_sub(self):
        self.bg_sub = cv2.BackgroundSubtractorMOG2()
        self.bg_sub.setDouble('nShadowDetection', 0)
        self.bg_sub.setDouble('history', 25)

        return self

    def get_distinct_contour_bounds(self, frame):
        bounds = self.get_all_contour_bounds(frame)
        bounds.sort(key=lambda b: b[2] * b[3])

        # Remove all bounds that are within other bounds
        i = 0
        while i + 1 < len(bounds):
            for j in xrange(len(bounds) - 1, i, -1):
                if is_within(bounds[i], bounds[j]):
                    bounds.pop(i)
                    break
            i += 1

        return bounds

    # Runs background subtraction on the given frame to identify the areas of
    # the frame that have altered over time. Returns bounded rectangles over
    # those contours.
    def get_all_contour_bounds(self, frame):
        frameblur = cv2.blur(frame, (5, 5))
        fg_mask = self.bg_sub.apply(frameblur, self.learning_rate)
        cv2.imshow('bgsub', fg_mask)

        contours, hier = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_SIMPLE)

        bounds = map(cv2.boundingRect, contours)
        bounds = filter(lambda b: (b[2] > self.min_size) & (b[3] > self.min_size), bounds)
        bounds = filter(lambda b: b[3] > self.height_width_ratio * b[2], bounds)

        return bounds

