from chunk import Chunk

import pyaudio
import numpy as np

# AUDIO PARAMETERS
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 1024
DURATION = 1
FREQUENCY = 1

# Initialize PyAudio
p = pyaudio.PyAudio()

# Generate the sine wave
num_samples = int(RATE * DURATION)

t = np.linspace(0.)