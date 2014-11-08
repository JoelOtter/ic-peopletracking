import cv2
import sys

# Argument parsing
if len(sys.argv) > 2:
    sys.exit("Too many arguments")
elif len(sys.argv) < 2:
    sys.exit("Too few arguments")

# Load video and check if opened
cap = cv2.VideoCapture(sys.argv[1])
if not cap.isOpened():
    sys.exit("Failed to load video")

num_frames = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
wait_per_frame = int(1/fps * 1000/1)

# Loop through each frame. Break on esc key
for i in xrange(num_frames):
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    k = cv2.waitKey(wait_per_frame) & 0xff
    if k == 27:
        break

# Close video and clean up
cap.release()
cv2.destroyAllWindows()
