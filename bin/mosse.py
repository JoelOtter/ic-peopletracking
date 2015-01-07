import numpy as np
import cv2


def inside(r, q):
    rx, ry, rw, rh = r
    qx, qy, qw, qh = q
    return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh


def draw_detections(img, rects, thickness=1):
    for x, y, w, h in rects:
        # the HOG detector returns slightly larger rectangles than the real
        # objects.
        # so we slightly shrink the rectangles to get a nicer output.
        pad_w, pad_h = int(0.15 * w), int(0.05 * h)
        cv2.rectangle(img, (x + pad_w, y + pad_h),
                      (x + w - pad_w, y + h - pad_h),
                      (0, 255, 0), thickness)


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


def rnd_warp(a):
    h, w = a.shape[:2]
    T = np.zeros((2, 3))
    coef = 0.2
    ang = (np.random.rand() - 0.5) * coef
    c, s = np.cos(ang), np.sin(ang)
    T[:2, :2] = [[c, -s], [s, c]]
    T[:2, :2] += (np.random.rand(2, 2) - 0.5) * coef
    c = (w / 2, h / 2)
    T[:, 2] = c - np.dot(T[:2, :2], c)
    return cv2.warpAffine(a, T, (w, h), borderMode=cv2.BORDER_REFLECT)


def divSpec(A, B):
    Ar, Ai = A[..., 0], A[..., 1]
    Br, Bi = B[..., 0], B[..., 1]
    C = (Ar + 1j * Ai) / (Br + 1j * Bi)
    C = np.dstack([np.real(C), np.imag(C)]).copy()
    return C


def draw_str(dst, (x, y), s):
    cv2.putText(dst, s, (x + 1, y + 1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0),
                thickness=2, lineType=8)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255),
                lineType=8)

eps = 1e-5


class MOSSE:
    def __init__(self, frame, rect):
        x1, y1, x2, y2 = rect
        w, h = map(cv2.getOptimalDFTSize, [x2 - x1, y2 - y1])
        x1, y1 = (x1 + x2 - w) // 2, (y1 + y2 - h) // 2
        self.pos = x, y = x1 + 0.5 * (w - 1), y1 + 0.5 * (h - 1)
        self.size = w, h
        img = cv2.getRectSubPix(frame, (w, h), (x, y))

        self.win = cv2.createHanningWindow((w, h), cv2.CV_32F)
        g = np.zeros((h, w), np.float32)
        g[h // 2, w // 2] = 1
        g = cv2.GaussianBlur(g, (-1, -1), 2.0)
        g /= g.max()

        self.G = cv2.dft(g, flags=cv2.DFT_COMPLEX_OUTPUT)
        self.H1 = np.zeros_like(self.G)
        self.H2 = np.zeros_like(self.G)
        for i in xrange(128):
            a = self.preprocess(rnd_warp(img))
            A = cv2.dft(a, flags=cv2.DFT_COMPLEX_OUTPUT)
            self.H1 += cv2.mulSpectrums(self.G, A, 0, conjB=True)
            self.H2 += cv2.mulSpectrums(A, A, 0, conjB=True)
        self.update_kernel()
        self.update(frame)

    def returnCentre(self):
        return self.pos

    def update(self, frame, rate=0.125):
        (x, y), (w, h) = self.pos, self.size
        self.last_img = img = cv2.getRectSubPix(frame, (w, h), (x, y))
        img = self.preprocess(img)
        self.last_resp, (dx, dy), self.psr = self.correlate(img)
        self.good = self.psr > 8.0
        if not self.good:
            return

        self.pos = x + dx, y + dy
        self.last_img = img = cv2.getRectSubPix(frame, (w, h), self.pos)
        img = self.preprocess(img)

        A = cv2.dft(img, flags=cv2.DFT_COMPLEX_OUTPUT)
        H1 = cv2.mulSpectrums(self.G, A, 0, conjB=True)
        H2 = cv2.mulSpectrums(A, A, 0, conjB=True)
        self.H1 = self.H1 * (1.0 - rate) + H1 * rate
        self.H2 = self.H2 * (1.0 - rate) + H2 * rate
        self.update_kernel()

    @property
    def state_vis(self):
        f = cv2.idft(self.H, flags=cv2.DFT_SCALE | cv2.DFT_REAL_OUTPUT)
        h, w = f.shape
        f = np.roll(f, -h // 2, 0)
        f = np.roll(f, -w // 2, 1)
        kernel = np.uint8((f - f.min()) / f.ptp() * 255)
        resp = self.last_resp
        resp = np.uint8(np.clip(resp / resp.max(), 0, 1) * 255)
        vis = np.hstack([self.last_img, kernel, resp])
        return vis

    def draw_state(self, vis):
        (x, y), (w, h) = self.pos, self.size
        x1, y1 = int(x - 0.5 * w), int(y - 0.5 * h)
        x2, y2 = int(x + 0.5 * w), int(y + 0.5 * h)
        cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 0, 255))
        if self.good:
            cv2.circle(vis, (int(x), int(y)), 2, (0, 0, 255), -1)
        else:
            cv2.line(vis, (x1, y1), (x2, y2), (0, 0, 255))
            cv2.line(vis, (x2, y1), (x1, y2), (0, 0, 255))
        draw_str(vis, (x1, y2 + 16), 'PSR: %.2f' % self.psr)

    def preprocess(self, img):
        img = np.log(np.float32(img) + 1.0)
        img = (img - img.mean()) / (img.std() + eps)
        return img * self.win

    def correlate(self, img):
        C = cv2.mulSpectrums(cv2.dft(img, flags=cv2.DFT_COMPLEX_OUTPUT),
                             self.H, 0, conjB=True)
        resp = cv2.idft(C, flags=cv2.DFT_SCALE | cv2.DFT_REAL_OUTPUT)
        h, w = resp.shape
        _, mval, _, (mx, my) = cv2.minMaxLoc(resp)
        side_resp = resp.copy()
        cv2.rectangle(side_resp, (mx - 5, my - 5), (mx + 5, my + 5), 0, -1)
        smean, sstd = side_resp.mean(), side_resp.std()
        psr = (mval - smean) / (sstd + eps)
        return resp, (mx - w // 2, my - h // 2), psr

    def update_kernel(self):
        self.H = divSpec(self.H1, self.H2)
        self.H[..., 1] *= -1


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
                fgmask = back_sub.apply(frameblur, learningRate=0.005)
                contours, hier = cv2.findContours(fgmask, cv2.RETR_EXTERNAL,
                                                  cv2.CHAIN_APPROX_SIMPLE)
                bounds = map(cv2.boundingRect, contours)

                hog = cv2.HOGDescriptor()

                hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector()
                                   )
                frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                for bound in bounds:
                    bx, by, bw, bh = bound
                    cx = bx + (1.3 * bw / 2)
                    cy = by + (1.5 * by / 2)
                    likely_same = False
                    for tracker in self.trackers:
                        x, y = tracker.pos
                        if((cx < x + 70 or cx < x - 70) and
                                (cy < y + 100 or cy < y - 100)):
                            likely_same = True
                            break

                    if likely_same:
                        break

                    if bw > 30 and bh > 3 * bw and bh > 70:
                        crop_img = self.frame[by:by + 1.1 * bh,
                                              bx:bx + 1.1 * bw]
                        found, w = hog.detect(crop_img,
                                              winStride=(8, 8),
                                              padding=(32, 32))
                        if found is not None:
                            x1 = int(bx - 0.3 * bw)
                            x2 = int(bx + 1.5 * bw)
                            y2 = int(by + 1.5 * bh)
                            y1 = int(by - 0.7 * bh)
                            bound = x1, y1, x2, y2
                            cv2.rectangle(self.frame, (bx, by), ((bx + bw),
                                          (by + bh)), (0, 255, 0), 3)
                            tracker = MOSSE(frame_gray, bound)
                            self.trackers.append(tracker)

                for tracker in self.trackers:
                    tracker.update(frame_gray)
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
