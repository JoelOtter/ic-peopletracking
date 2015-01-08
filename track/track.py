import cv2
import json


def _setup_capture(source):
    return cv2.VideoCapture(source)


def _setup_background_subtractor():
    back_sub = cv2.BackgroundSubtractorMOG2()
    back_sub.setDouble('nShadowDetection', 0)
    back_sub.setDouble('history', 25)
    return back_sub


def _bigger_box(b1, b2):
    b1x, b1y, b1w, b1h = b1
    b2x, b2y, b2w, b2h = b2
    if b1w * b1h > b2w * b2h:
        return b1
    else:
        return b2


def JSON_from_video(source, width=0, height=0, show_images=False):

    def show_image(name, image):
        if show_images:
            cv2.imshow(name, image)

    cap = _setup_capture(source)

    def resize(frame, width, height):
        if height == 0 and width == 0:
            return frame

        feed_height = float(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
        feed_width = float(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))

        if height == 0:
            height = feed_height * width / feed_width
            height = int(height)
        if width == 0:
            width = feed_width * height / feed_height
            width = int(width)

        return cv2.resize(frame, (width, height))

    back_sub = _setup_background_subtractor()
    frame_no = 0
    frames = []
    while(True):
        ret, frame = cap.read()

        if not ret:
            break

        frame = resize(frame, width, height)

        frameblur = cv2.blur(frame, (5, 5))
        fgmask = back_sub.apply(frameblur, learningRate=0.001)

        show_image('contours', fgmask)

        contours, hier = cv2.findContours(fgmask, cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_SIMPLE)

        bounds = map(cv2.boundingRect, contours)

        if bounds:
            frame_data = {}
            frame_data['frame'] = frame_no
            bx, by, bw, bh = reduce(_bigger_box, bounds)
            cv2.rectangle(frame, (bx, by), ((bx + bw), (by + bh)),
                          (0, 255, 0), 3)
            frame_data['rectangles'] = [{'id': '',
                                         'x': bx,
                                         'y': by,
                                         'width': bw,
                                         'height': bh}]
            print frame_data

            frames.append(frame_data)

        show_image('input', frame)
        frame_no += 1

        if show_images:
            k = cv2.waitKey(1) & 0xff
            if k == 27:
                break

    cap.release()
    cv2.destroyAllWindows()
    return json.dumps(frames)
