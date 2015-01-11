import cv2


# Returns true if a is a bound that lies within b.
def is_within(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b

    return (bx <= ax) & (ax + aw <= bx + bw) &\
           (by <= ay) & (ay + ah <= by + bh)


# Returns true if a point (a) lies inside the bound.
def is_inside(a, bound):
    ax, ay = a
    bx, by, bw, bh = bound

    return (bx <= ax) & (ax <= bx + bw) &\
           (by <= ay) & (ay <= by + bh)


class HumanTracker:

    def __init__(self, height_width_ratio=3, learning_rate=0.005):

        """
        Parameters
        ----------
        height_width_ratio: float, optional
        If this is set to N, then will discount all bounds that do not satisfy
        height > N * width.

        learning_rate: float, optional
        Rate at which background changes are assimilated into the background
        average.
        """

        self.learning_rate = learning_rate
        self.height_width_ratio = height_width_ratio

        (
            self
            .init_bg_sub()
            .init_hog()
        )

    def init_bg_sub(self):
        self.bg_sub = cv2.BackgroundSubtractorMOG2()
        self.bg_sub.setDouble('nShadowDetection', 0)
        self.bg_sub.setDouble('history', 25)

        return self

    def init_hog(self):
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        return self

    def get_human_bounds(self, frame, ignore_positions=[], ignore_eps=20):

        """
        Parameters
        ----------
        ignore_positions: list of (x,y), optional
        An optional filter before HOG detection. Filters candidate bounds to
        remove any that cover any of these x,y co-ordinates.

        ignore_eps: int, optional
        Optional epsilon value for computing ignore positions. Will pad each
        bound by the given value.
        """

        bounds = self.get_distinct_contour_bounds(frame)
        bounds = filter(lambda b: b[3] > self.height_width_ratio * b[2], bounds)
        bounds = filter(lambda b: not any(map(lambda x: is_inside(x, b), ignore_positions)), bounds)
        bounds = filter(lambda b: self.is_bound_human(b, frame), bounds)

        return bounds

    def is_bound_human(self, bound, frame):
        bx, by, bw, bh = bound
        pad_w, pad_h = map(lambda d: int(0.15 * d), [bw, bh])

        padded_crop = frame[max(0, by - pad_h):(by + bh + pad_h),
                            max(0, bx - pad_w):(bx + bw + pad_w)]

        found, w = self.hog.detectMultiScale(padded_crop, winStride=(8, 8), padding=(32, 32))
        return found is not None

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

        contours, hier = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_SIMPLE)

        bounds = map(cv2.boundingRect, contours)
        return filter(lambda b: (b[2] > 20) & (b[3] > 20), bounds)


