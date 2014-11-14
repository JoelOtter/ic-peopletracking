#!/usr/bin/python
import cv2
import cv2.cv as cv
import sys

cap = None
back_sub = None


def setup_capture():
    global cap
    if len(sys.argv) > 1:
        cap = cv2.VideoCapture(sys.argv[1])
    else:
        cap = cv2.VideoCapture(0)


def setup_background_subtractor():
    global back_sub
    back_sub = cv2.BackgroundSubtractorMOG2()
    back_sub.setDouble('nShadowDetection', 0)
    back_sub.setDouble('history', 25)


def bigEnough((bx, by, bw, bh)):
    return bw*bh > 5000

setup_capture()
setup_background_subtractor()

while(1):
    ret, frame = cap.read()
    cv2.imshow('input', frame)
    frameblur = cv2.blur(frame, (5, 5))
    fgmask = back_sub.apply(frameblur, learningRate=0.005)

    cv2.imshow('backgroundsubtraction', fgmask)
    contours, hier = cv2.findContours(fgmask, cv2.RETR_EXTERNAL,
                                      cv2.CHAIN_APPROX_SIMPLE)

    bounds = filter(bigEnough, (map(cv2.boundingRect, contours)))

    for bx, by, bw, bh in bounds:
        cv2.rectangle(frame, (bx, by), ((bx + bw), (by + bh)), (0, 255, 0), 3)

    cv2.imshow('bounds', frame)

    k = cv2.waitKey(3) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
