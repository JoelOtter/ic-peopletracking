import numpy as np
import cv2
from track.mosse import MOSSE


def _setup_background_subtractor():
    back_sub = cv2.BackgroundSubtractorMOG2()
    back_sub.setDouble('nShadowDetection', 0)
    back_sub.setDouble('history', 25)
    return back_sub


class RectSelector:
    def __init__(self, win, callback):
        self.win = win
        self.callback = callback
        cv2.setMouseCallback(win, self.onmouse)
        self.drag_start = None
        self.drag_rect = None

    def onmouse(self, event, x, y, flags, param):
        x, y = np.int16([x, y])

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
        if self.drag_start:
            if flags & cv2.EVENT_FLAG_LBUTTON:
                xo, yo = self.drag_start
                x0, y0 = np.minimum([xo, yo], [x, y])
                x1, y1 = np.maximum([xo, yo], [x, y])
                self.drag_rect = None
                if x1 - x0 > 0 and y1 - y0 > 0:
                    self.drag_rect = (x0, y0, x1, y1)
            else:
                rect = self.drag_rect
                self.drag_start = None
                self.drag_rect = None
                if rect:
                    self.callback(rect)

    def draw(self, vis):
        if not self.drag_rect:
            return False
        x0, y0, x1, y1 = self.drag_rect
        cv2.rectangle(vis, (x0, y0), (x1, y1), (0, 255, 0), 2)
        return True

    @property
    def dragging(self):
        return self.drag_rect is not None


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
        back_sub = _setup_background_subtractor()
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector()
                           )
        while True:
            if not self.paused:
                ret, self.frame = self.cap.read()
                self.frame = cv2.resize(self.frame, (854, 480))
                # cv2.rectangle(self.frame, (400, 0), (450, 480),
                # (0, 255, 255), -1)
                if not ret:
                    break
                # contour code
                frameblur = cv2.blur(self.frame, (5, 5))
                # Learning rate at 0.005 to increase response to still humans
                fgmask = back_sub.apply(frameblur, learningRate=0.005)
                contours, hier = cv2.findContours(fgmask, cv2.RETR_EXTERNAL,
                                                  cv2.CHAIN_APPROX_SIMPLE)
                bounds = map(cv2.boundingRect, contours)

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
