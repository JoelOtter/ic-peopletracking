# Test creation tool

This is a simple web tool to create sample test data, built with Flask and jQuery. To use:

- Run the following commands in your virtualenv:
    ```
    pip install -r requirements.txt
    bower install
    ```
- Run the testcreator.py script.
- Go to localhost:5000/create/*folder*/*file*, where *folder* is the video folder and *file* is the specific video.
    For example, if I wanted to create a test for the video at across/normal.mp4, I'd go to localhost:5000/across/normal.
- Follow the person on screen using your mouse. The video auto-plays. If you're not happy with the results, just refresh the page - nothing gets written to file until you click the button.

The tool assumes that the test videos are located in [project root]/tests/videos, in their respective folders, e.g. across/normal.mp4.

---

## Viewer

There is also a viewer located at localhost:5000/view. Just select a video and a JSON file, and hit the space bar.
