import numpy as np
import cv2


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


def div_spec(A, B):
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


class MOSSE:

    # Initialise new MOSSE tracker.
    #   target_rect: surrounding co-ordinates of initial rectangle to track
    def __init__(self, frame, target_rect, eps=1e-5):
        self.same = 0
        self.bad_count = 0
        self.eps = eps
        self.dy, self.dx = 0, 0

        (
            self
            .init_target(target_rect)
            .init_gaussian_identity()
            .init_hanning_window()
            .init_training_data(frame)
        )

    # Given a target rectangle representing the object to track, will set
    # instance fields size and position, representing a rectangle overlay
    # frame to track within the video.
    def init_target(self, target_rect):
        x1, y1, x2, y2 = target_rect
        self.size = w, h = map(cv2.getOptimalDFTSize, [x2 - x1, y2 - y1])

        x1, y1 = (x1 + x2 - w) // 2, (y1 + y2 - h) // 2
        self.position = x, y = x1 + 0.5 * (w - 1), y1 + 0.5 * (h - 1)

        return self

    # Initialises self.G, the basis array on which to correlate differences
    # between targets in frames.
    def init_gaussian_identity(self):
        w, h = self.size
        g = np.zeros((h, w), np.float32)
        g[h // 2, w // 2] = 1
        g = cv2.GaussianBlur(g, (-1, -1), 2.0)
        g /= g.max()  # normalise array

        self.G = cv2.dft(g, flags=cv2.DFT_COMPLEX_OUTPUT)

        return self

    # Generates hanning window that is used to perform calculations with img
    def init_hanning_window(self):
        self.win = cv2.createHanningWindow(tuple(self.size), cv2.CV_32F)
        return self

    # Creates the initial H1 & H2 transforms of correlation filters
    def init_training_data(self, frame, count=128):
        img = self.get_target_img_from_frame(frame)
        self.H1 = np.zeros_like(self.G)
        self.H2 = np.zeros_like(self.G)

        for i in xrange(128):
            a = self.preprocess(rnd_warp(img))
            A = cv2.dft(a, flags=cv2.DFT_COMPLEX_OUTPUT)
            self.H1 += cv2.mulSpectrums(self.G, A, 0, conjB=True)
            self.H2 += cv2.mulSpectrums(A, A, 0, conjB=True)

        self.update_kernel()
        self.update(frame)

        return self

    # Updates filter with new correlation difference
    def update_kernel(self):
        self.H = div_spec(self.H1, self.H2)
        self.H[..., 1] *= -1

    # Given a frame, returns an image that is the contents of the frame
    # contained within the target.
    def get_target_img_from_frame(self, frame):
        return cv2.getRectSubPix(frame, tuple(self.size), tuple(self.position))

    # Update tracker with the given new frame. Should a correlation succeed,
    # will update filters and adjust for new tracked position.
    def update(self, frame, rate=0.125):
        img = self.process_new_img(frame)
        self.last_resp, (dx, dy), self.psr = self.correlate(img)
        self.good = self.psr > 8.0
        if not self.good:
            self.bad_count += 1
            return

        x, y = self.position
        self.position = x + dx, y + dy

        img = self.process_new_img(frame)

        A = cv2.dft(img, flags=cv2.DFT_COMPLEX_OUTPUT)
        H1 = cv2.mulSpectrums(self.G, A, 0, conjB=True)
        H2 = cv2.mulSpectrums(A, A, 0, conjB=True)
        self.H1 = self.H1 * (1.0 - rate) + H1 * rate
        self.H2 = self.H2 * (1.0 - rate) + H2 * rate
        self.update_kernel()

    # Assigns target image to the self.last_img memory field, returning the
    # new processed frame.
    def process_new_img(self, frame):
        self.last_img = self.get_target_img_from_frame(frame)
        return self.preprocess(self.last_img)

    # Modifies the image to be less sensitive to low-contrast environments,
    # and places importance on matching elements in the center of the target
    # over those at the edge. Ref [3]
    def preprocess(self, img):
        img = np.log(np.float32(img) + 1.0)
        img = (img - img.mean()) / (img.std() + self.eps)
        return img * self.win

    # Performs correlation using filter H on the given img.
    def correlate(self, img):
        C = cv2.mulSpectrums(cv2.dft(img, flags=cv2.DFT_COMPLEX_OUTPUT),
                             self.H, 0, conjB=True)
        resp = cv2.idft(C, flags=cv2.DFT_SCALE | cv2.DFT_REAL_OUTPUT)
        h, w = resp.shape
        _, mval, _, (mx, my) = cv2.minMaxLoc(resp)
        side_resp = resp.copy()
        cv2.rectangle(side_resp, (mx - 5, my - 5), (mx + 5, my + 5), 0, -1)
        smean, sstd = side_resp.mean(), side_resp.std()
        psr = (mval - smean) / (sstd + self.eps)
        return resp, (mx - w // 2, my - h // 2), psr

    # Draws rectangle round the currently tracked position.
    def draw_state(self, vis):
        (x, y), (w, h) = self.position, self.size
        x1, y1 = int(x - 0.5 * w), int(y - 0.5 * h)
        x2, y2 = int(x + 0.5 * w), int(y + 0.5 * h)
        cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 0, 255))
        if self.good:
            cv2.circle(vis, (int(x), int(y)), 2, (0, 0, 255), -1)
        else:
            cv2.line(vis, (x1, y1), (x2, y2), (0, 0, 255))
            cv2.line(vis, (x2, y1), (x1, y2), (0, 0, 255))
        draw_str(vis, (x1, y2 + 16), 'PSR: %.2f' % self.psr)

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

