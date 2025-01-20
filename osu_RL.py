import torch as th
from stable_baselines3 import PPO
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.vec_env import DummyVecEnv
from custom_gym import OsuEnv
import gym
from screen_shot import ScreenCapture


class SimpleCNN(BaseFeaturesExtractor):
    """
    A simple custom CNN feature extractor for grayscale inputs of shape (1, H, W).
    We will produce a feature vector that PPO can use.
    """
    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 256):
        super(SimpleCNN, self).__init__(observation_space, features_dim)
        # The shape is (1, height, width), let's get height and width
        self.c, self.h, self.w = observation_space.shape

        self.cnn = th.nn.Sequential(
            th.nn.Conv2d(self.c, 16, kernel_size=5, stride=2, padding=2),
            th.nn.ReLU(),
            th.nn.Conv2d(16, 32, kernel_size=5, stride=2, padding=2),
            th.nn.ReLU(),
            th.nn.Flatten()
        )

        # Compute shape by doing one forward pass
        with th.no_grad():
            sample = th.as_tensor(observation_space.sample()[None]).float()
            n_flatten = self.cnn(sample).shape[1]

        self.linear = th.nn.Sequential(
            th.nn.Linear(n_flatten, features_dim),
            th.nn.ReLU()
        )

        self._features_dim = features_dim

    def forward(self, observations: th.Tensor) -> th.Tensor:
        x = self.cnn(observations)
        x = self.linear(x)
        return x

def train_osu_agent():
    # 1. Initialize our screen capture
    screen_capture = ScreenCapture(monitor_region=None, scale=4)

    # 2. Determine final frame shape after downscale
    # If 1920x1080 => downscale by 4 => (480, 270)
    final_width = 1920 // 4
    final_height = 1080 // 4

    # 3. Create the environment
    env = OsuEnv(screen_capture, width=final_width, height=final_height)

    # 4. Stable Baselines requires a vectorized environment
    vec_env = DummyVecEnv([lambda: env])

    # 5. Make a custom policy that uses our SimpleCNN
    policy_kwargs = dict(
        features_extractor_class=SimpleCNN,
        features_extractor_kwargs=dict(features_dim=128),  # dimension of final layer
    )

    # 6. Create the PPO model
    model = PPO(
        "CnnPolicy",
        vec_env,
        policy_kwargs=policy_kwargs,
        verbose=1,
        learning_rate=1e-4,
        n_steps=512,  # how many steps to collect before each update
        batch_size=64,
        tensorboard_log="./tensorboard_log"
    )

    # 7. Train the model
    # WARNING: In a real scenario, each "step" might be a real-time second (or fraction).
    # This could take hours/days. Here we just show how you'd start training.
    model.learn(total_timesteps=10_000)  # Example small number

    # 8. (Optional) Save the model
    model.save("osu_ppo_model")

    print("Training complete!")

if __name__ == "__main__":
    train_osu_agent()
