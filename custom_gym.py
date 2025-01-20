import gym
import pyautogui
import numpy as np

from gym import spaces

class OsuEnv(gym.Env):
    """
    A custom Gym Environment that interacts with the real Osu game using screen capture and mouse input.
    """
    def __init__(self, screen_capture, width, height):
        super(OsuEnv, self).__init__()

        # Save the screen capture utility
        self.screen_capture = screen_capture
        self.width = width
        self.height = height

        # Observation space:
        # We have a single grayscale frame of shape (height, width).
        # Gym typically uses (Channels, Height, Width) for images, so let's do that.
        # We'll store them as floats in [0, 255].
        self.observation_space = spaces.Box(
            low=0, high=255,
            shape=(1, self.height, self.width),
            dtype=np.uint8
        )

        # Action space (continuous):
        # Let's define 3 continuous actions:
        # 1) Move X in range [-1, 1]
        # 2) Move Y in range [-1, 1]
        # 3) Click "strength" in [0, 1], where <0.5 => no click, >=0.5 => click
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0, 0.0]),
            high=np.array([1.0, 1.0, 1.0]),
            shape=(3,),
            dtype=np.float32
        )

        # We might keep track of old score so we can measure reward changes
        self.old_score = 0

    def reset(self):
        """
        Here we should 'reset' the game state.
        But since it's a real game, we might have to manually:
        - Open the map or wait at the start of the song
        - Possibly use pyautogui to navigate menus

        For now, let's just capture an initial frame and treat that as the first observation.
        """
        # You could do something like pyautogui.press('esc') or pyautogui.click() 
        # to navigate the Osu menu if needed, or do nothing if the game is already at the start.

        # Grab a first frame from the screen
        frame = self.screen_capture.grab_frame()

        # Reset old_score to 0 for a new episode
        self.old_score = 0

        # Return observation in channel-first format: (1, height, width)
        obs = frame[np.newaxis, :, :]
        return obs

    def step(self, action):
        """
        action: [move_x, move_y, click_strength]
        Each step, we will move the mouse a little bit, 
        optionally click if click_strength >= 0.5,
        then capture a new frame, and compute a reward.
        """
        move_x, move_y, click_strength = action

        # 1. Convert move_x, move_y in [-1, 1] to actual screen coordinates offsets.
        #    Let's define how big each step can be. For example, up to +/- 50 pixels.
        max_movement = 50
        dx = int(move_x * max_movement)
        dy = int(move_y * max_movement)

        # Get current mouse position
        current_x, current_y = pyautogui.position()

        # Move to new position
        new_x = current_x + dx
        new_y = current_y + dy
        pyautogui.moveTo(new_x, new_y)

        # 2. Handle click
        # If click_strength >= 0.5, we do a mouse down & up quickly (a click).
        # This is a naive approach. A more advanced approach might hold down, etc.
        if click_strength >= 0.5:
            pyautogui.click()

        # 3. Grab new frame as next observation
        frame = self.screen_capture.grab_frame()
        obs = frame[np.newaxis, :, :]

        # 4. Compute reward
        # We do a placeholder approach that tries to read some "score" from the image.
        # For now, let's pretend we have a function that returns the current score as an integer.
        current_score = self._get_score_from_image(frame)

        # The reward is the change in score
        reward = current_score - self.old_score
        self.old_score = current_score

        # 5. Check if the episode is done (for example, if the song ends).
        # We'll do a placeholder that ends after some fixed number of steps.
        done = False  # You might detect a "results screen" in the image, or read the time.

        # 6. Info dict (optional debug info)
        info = {}

        return obs, reward, done, info

    def render(self, mode='human'):
        """
        If you want to display frames or debugging info, do it here.
        For example, you could show the last grabbed frame in a window with OpenCV.
        """
        pass

    def _get_score_from_image(self, frame):
        """
        Placeholder function to parse the score from the grayscale frame.
        You'd need advanced techniques (OCR, template matching, region-of-interest reading).
        For now, we'll just return 0 or a dummy score.
        """
        # Example: always return 0.
        # Replace with real detection logic if you want a real reward.
        return 0
