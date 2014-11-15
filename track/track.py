import cv2
import json

cap = None
back_sub = None


def _setup_capture(source):
    global cap
    cap = cv2.VideoCapture(source)


def _setup_background_subtractor():
    global back_sub
    back_sub = cv2.BackgroundSubtractorMOG2()
    back_sub.setDouble('nShadowDetection', 0)
    back_sub.setDouble('history', 25)


def _bigger_box(b1, b2):
    b1x, b1y, b1w, b1h = b1
    b2x, b2y, b2w, b2h = b2
    if b1w*b1h > b2w*b2h:
        return b1
    else:
        return b2


def JSON_from_video(source):
    _setup_capture(source)
    _setup_background_subtractor()
    frame_no = 0
    frames = []
    while(True):
        ret, frame = cap.read()

        if not ret:
            break

        frameblur = cv2.blur(frame, (5, 5))
        fgmask = back_sub.apply(frameblur, learningRate=0.001)

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
            frames.append(frame_data)

        frame_no += 1

    cap.release()
    cv2.destroyAllWindows()
    return json.dumps(frames)
