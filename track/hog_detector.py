import cv2
import helpers


class HOGDetector:

    def __init__(self, win_stride=(8, 8), padding=(32, 32)):

        """
        Parameters
        ----------
        win_stride: (int, int), optional
        Defines axes overlaps for sliding window searches. OpenCV param.

        padding: (int, int), optional
        Pads the candidate crop to allow for searching near image edges. Best
        values are a multiple of win_stride.
        """

        self.win_stride = win_stride
        self.padding = padding

        self.min_width, self.min_height = [
            win_stride[0] + padding[0],
            win_stride[1] + padding[1]
        ]

        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def select_human_bounds(self, frame, bounds):
        return filter(lambda b: self.is_bound_human(b, frame), bounds)

    def is_bound_human(self, bound, frame):
        bx, by, bw, bh = bound

        if (bw <= self.min_width) or (bh <= self.min_height):
            return False

        pad_w, pad_h = map(lambda d: int(0.3 * d), [bw, bh])

        padded_crop = frame[max(0, by - pad_h):(by + bh + pad_h),
                            max(0, bx - pad_w):(bx + bw + pad_w)]

        found, w = self.hog.detectMultiScale(
            padded_crop,
            winStride=self.win_stride,
            padding=self.padding,
            scale=1.05
        )

        return found is not None



