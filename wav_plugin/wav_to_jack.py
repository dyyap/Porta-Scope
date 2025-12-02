import jack
import numpy as np

# Audio Parameters
samplerate = 160000
freq = 28000
duration = 1
amplitude = .5

# Generate the sine wave #Replace later
t = np.linspace(0, duration, int(duration * samplerate))
sine_wave = amplitude * np.sin(2* np.pi * freq * t)

# Initialize JACK Client
client = jack.Client("SINEWAVE_EXAMPLE")

# Register the outport
output_port = client.outports.register('output_1')
# Define the process callback

def process(frames):
    # Get the output buffer
    out_buffer = output_port.get_buffer()

    #Fill the buffer with the sinewave data
    # buffer_size == frames && data == float32
    out_buffer[:] = sine_wave[client.frame_time % len(sine_wave) : (client.frame_time % len(sine_wave)) + frames].astype(np.float32)

    return 0

# Activate the client
client.activate()

print("Playing the SINE WAV")

try:
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping SINE WAV")
finally:
    client.deactivate()
    client.close()