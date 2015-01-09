import cv2
import json
import cv2.cv as cv
import numpy as np


def drawCross(img, center, r, g, b):
    d = 5
    t = 2
    color = (r, g, b)
    ctrx = int(center[0])
    ctry = int(center[1])
    cv2.line(img, (ctrx - d, ctry - d), (ctrx + d, ctry + d), color, t)
    cv2.line(img, (ctrx + d, ctry - d), (ctrx - d, ctry + d), color, t)


def drawLines(img, points, r, g, b):
    cv2.polylines(img, [np.int32(points)], isClosed=False, color=(r, g, b))


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


def JSON_from_video(source):
    cap = _setup_capture(source)
    wait_per_frame = int(1000 / int(cap.get(cv2.cv.CV_CAP_PROP_FPS)))
    back_sub = _setup_background_subtractor()
    frame_no = 0
    threshold = 100
    frames = []

    # Set up the kalman filter
    processNoiseCovariance = 1e-5
    measurementNoiseCovariance = 1e-1
    errorCovariancePost = 0.1
    kalman = cv.CreateKalman(4, 2, 0)
    kalman_measurement = cv.CreateMat(2, 1, cv.CV_32FC1)
    found = False

    cv.SetIdentity(kalman.measurement_matrix, cv.RealScalar(1))
    cv.SetIdentity(kalman.process_noise_cov,
                   cv.RealScalar(processNoiseCovariance))
    cv.SetIdentity(kalman.measurement_noise_cov,
                   cv.RealScalar(measurementNoiseCovariance))
    cv.SetIdentity(kalman.error_cov_post, cv.RealScalar(errorCovariancePost))

    # This will hold our estimated point value
    estimated = None

    # These will get the trajectories for mouse location and Kalman estiamte
    kalman_points = []
    # set kalman transition matrix
    kalman.transition_matrix[0, 0] = 1
    kalman.transition_matrix[0, 1] = 0
    kalman.transition_matrix[0, 2] = 1
    kalman.transition_matrix[0, 3] = 0
    kalman.transition_matrix[1, 0] = 0
    kalman.transition_matrix[1, 1] = 1
    kalman.transition_matrix[1, 2] = 0
    kalman.transition_matrix[1, 3] = 0
    kalman.transition_matrix[2, 0] = 0
    kalman.transition_matrix[2, 1] = 0
    kalman.transition_matrix[2, 2] = 0
    kalman.transition_matrix[2, 3] = 1
    kalman.transition_matrix[3, 0] = 0
    kalman.transition_matrix[3, 1] = 0
    kalman.transition_matrix[3, 2] = 0
    kalman.transition_matrix[3, 3] = 1
    prev_x = None

    while(True):
        found = False
        ret, frame = cap.read()

        if not ret:
            break
        
        cv2.rectangle(frame, (400,0), (454, 480), (0, 255, 255), -1)
        frameblur = cv2.blur(frame, (5, 5))
        fgmask = back_sub.apply(frameblur, learningRate=0.001)
        #cv2.imshow('bg', fgmask)
        contours, hier = cv2.findContours(fgmask, cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_SIMPLE)

        bounds = map(cv2.boundingRect, contours)
       
        if bounds:
            frame_data = {}
            frame_data['frame'] = frame_no
            bx, by, bw, bh = reduce(_bigger_box, bounds)

            measured = (bx + bw / 2, by + bh / 2)

           # If i have found something vaguely human
            if 2 * bw < bh:
               curr_x = bx + bw / 2
               if prev_x is None or abs(curr_x - prev_x) < threshold:
                 found = True
                 cv2.rectangle(frame, (bx, by), ((bx + bw), (by + bh)),
                               (0, 255, 0), 3)
                 frame_data['rectangles'] = [{'id': '',
                                             'x': bx,
                                             'y': by,
                                             'width': bw,
                                             'height': bh}]
                 frames.append(frame_data)
            # I only update the value if it is correct and has been found.
            predicted = cv.KalmanPredict(kalman)
            drawCross(frame, (predicted[0, 0], predicted[1, 0]), 255, 0, 0)
            if found is True:
                # Update the Kalman filter with these mesaurements
                kalman_measurement[0, 0] = bx + bw / 2
                kalman_measurement[1, 0] = by + bh / 2
                # Predict and update the internals of the kalman
                
                # Corrrect the estimate
                corrected = cv.KalmanCorrect(kalman, kalman_measurement)
                estimated = (corrected[0, 0], corrected[1, 0])
                prev_x = predicted[0, 0]
                kalman_points.append(estimated)
                print 'predicted = ' + str(predicted[0,0])
                print 'corrected = ' + str(corrected[0,0])
                print 'measured  = ' + str(bx + bw / 2)

                # Display the trajectories and current points
                #drawLines(frame, kalman_points, 0, 255, 0)
                #drawCross(frame, estimated, 255, 255, 255)
                #drawCross(frame, measured, 0, 0, 255)
        
        cv2.imshow('frame', frame)
        key = cv2.waitKey(wait_per_frame) & 0xff
        if key == 27:
            return
        frame_no += 1

    cap.release()
    cv2.destroyAllWindows()
    return json.dumps(frames)
