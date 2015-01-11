import numpy as np
import cv2
from track.mosse import MOSSE


# Returns true is a is a bound that lies within b.
def is_within(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b

    return (bx <= ax) & (ax + aw <= bx + bw) &\
           (by <= ay) & (ay + ah <= by + bh)


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

    def get_human_bounds(self, frame, ignore_positions=[]):

        """
        Parameters
        ----------
        ignore_positions: list of (x,y), optional
        An optional filter before HOG detection. Filters candidate bounds to
        remove any that cover any of these x,y co-ordinates.
        """

        bounds = self.get_distinct_contour_bounds(frame)
        bounds = filter(lambda b: b[3] > self.height_width_ratio * b[2], bounds)

        # TODO

        return bounds

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

        return map(cv2.boundingRect, contours)


class Track:

    def __init__(self, video_src, paused=False, display=False):
        self.cap = cv2.VideoCapture(video_src)
        self.frame = self.next_frame()
        self.trackers = []
        self.paused = paused

        if display: cv2.imshow('frame', self.frame)

    def next_frame(self):
        _, frame = self.cap.read()
        return frame

    def onrect(self, rect):
        frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        tracker = MOSSE(frame_gray, rect)
        self.trackers.append(tracker)


class App:

    def __init__(self, video_src, paused=False):
        self.cap = cv2.VideoCapture(video_src)
        _, self.frame = self.cap.read()
        cv2.imshow('frame', self.frame)
        # self.rect_sel = RectSelector('frame', self.onrect)
        self.trackers = []
        self.paused = paused

    def onrect(self, rect):
        frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        tracker = MOSSE(frame_gray, rect)
        self.trackers.append(tracker)

    def run(self):
        human_tracker = HumanTracker()
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector()
                           )
        while True:
            if not self.paused:
                ret, self.frame = self.cap.read()
                self.frame = cv2.resize(self.frame, (854, 480))
                if not ret:
                    break
                bounds = human_tracker.get_human_bounds(self.frame)
                frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                for bound in bounds:
                    bx, by, bw, bh = bound
                    x1 = bx
                    x2 = int(bx + 1.5 * bw)
                    y1 = int(by - 0.5 * bh)
                    y2 = int(by + bh)

                    cx, cy = x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2

                    likely_same = False
                    for tracker in self.trackers:
                        x, y = tracker.position
                        # print x, y, cx, cy
                        if(cx < x + 30 and cx > x - 30 and
                           cy < y + 50 and cy > y - 50):
                            likely_same = True
                            break

                    if likely_same:
                        break

                    if bw > 30 and bh > 3 * bw and bh > 70:
                        crop_img = self.frame[by:by + 1.3 * bh,
                                              bx:bx + 1.3 * bw]
                        found, w = hog.detect(crop_img,
                                              winStride=(8, 8),
                                              padding=(32, 32))
                        if found is not None:
                            x1 = bx
                            x2 = int(bx + 1.5 * bw)
                            y1 = int(by - 0.5 * bh)
                            y2 = int(by + bh)
                            # print x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2
                            bound = x1, y1, x2, y2
                            cv2.rectangle(self.frame, (x1, y1), ((x2),
                                          (y2)), (0, 255, 0), 3)
                            tracker = MOSSE(frame_gray, bound)
                            self.trackers.append(tracker)

                for tracker in self.trackers[:]:
                    tracker.update(frame_gray)
                    if tracker.bad_count > 10:
                        self.trackers.remove(tracker)
                # end of contour code
            vis = self.frame.copy()
            for tracker in self.trackers:
                tracker.draw_state(vis)
            if len(self.trackers) > 0:
                cv2.imshow('tracker state', self.trackers[-1].state_vis)
            # self.rect_sel.draw(vis)

            cv2.imshow('frame', vis)
            ch = cv2.waitKey(10)
            if ch == 27:
                break
            if ch == ord(' '):
                self.paused = not self.paused
            if ch == ord('c'):
                self.trackers = []

if __name__ == '__main__':
    print __doc__
    import sys
    import getopt
    opts, args = getopt.getopt(sys.argv[1:], '', ['pause'])
    opts = dict(opts)
    try:
        video_src = args[0]
    except:
        video_src = '0'

    App(video_src, paused='--pause' in opts).run()
