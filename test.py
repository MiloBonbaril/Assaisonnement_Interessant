import torch
import collections
from TTS.api import TTS
from TTS.utils.radam import RAdam

# Add required globals to PyTorch's safe list
torch.serialization.add_safe_globals([RAdam, collections.defaultdict])

# Force PyTorch to load full model
def custom_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return torch_load_original(*args, **kwargs)

torch_load_original = torch.load
torch.load = custom_load

# Define text, model, and vocoder
text = "Bonne nuit aussi ! Au revoir !"
model_name = "tts_models/multilingual/multi-dataset/bark"
vocoder_path = "vocoder_models/universal/libri-tts/fullband-melgan"  # Better vocoder
output_path = "./speech.wav"

# Load and run TTS with improved vocoder
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tts = TTS(model_name, vocoder_path=vocoder_path).to(device)
tts.tts_to_file(text=text, file_path=output_path, speed=2, emotion="amused")

print(f"Speech saved to {output_path}")
