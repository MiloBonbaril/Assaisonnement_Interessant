import mss
import cv2
import numpy as np

class ScreenCapture:
    def __init__(self, monitor_region=None, scale=4):
        """
        monitor_region: A dict with 'top', 'left', 'width', 'height' for mss.
                        If None, we capture the entire primary monitor by default.
        scale: how much to reduce the resolution by (4 means 1920x1080 -> 480x270).
        """
        self.sct = mss.mss()
        if monitor_region is None:
            # By default, capture the primary monitor at 1920x1080
            self.monitor = self.sct.monitors[1]  # 1 is usually the primary monitor
        else:
            self.monitor = monitor_region
        self.scale = scale

    def grab_frame(self):
        """
        Capture the screen region, convert to grayscale, and downscale.
        Returns a numpy array of shape (H, W) in grayscale.
        """
        # 1. Capture the screenshot
        screenshot = self.sct.grab(self.monitor)

        # 2. Convert the raw BGRA data to a numpy array
        img = np.array(screenshot, dtype=np.uint8)

        # 3. Convert to grayscale
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

        # 4. Downscale
        height, width = gray_img.shape
        new_width = width // self.scale
        new_height = height // self.scale

        small_gray_img = cv2.resize(gray_img, (new_width, new_height), interpolation=cv2.INTER_AREA)

        return small_gray_img
