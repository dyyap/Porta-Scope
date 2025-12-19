import matplotlib.pyplot as plt
import matplotlib.animation as animation
from jinja2.compiler import generate
from matplotlib import style
import jack
import numpy as np
import threading
import time

from numba.core.compiler import compile_internal

raw_sample = []
counter = 0
counter_in = []

class AudioReceiver:
    def __init__(self, client_name="audio_receiver"):
        self.client = jack.Client(client_name)
        self.sample_rate = self.client.samplerate
        self.blocksize = self.client.blocksize

        # Create input and output ports
        self.input_port = self.client.inports.register('input')
        self.output_port = self.client.outports.register('output')

        # Audio processing parameters
        self.gain = 0.5
        self.buffer = []

        # Set the process callback
        self.client.set_process_callback(self.process_audio)

        # Set shutdown callback
        self.client.set_shutdown_callback(self.shutdown)

    def process_audio(self, frames):
        """Receive, process, and optionally forward audio data"""
        # Get input audio data
        input_data = self.input_port.get_array()

        # Process the audio (apply gain in this example)
        processed_data = input_data * self.gain

        print(processed_data)

        # Store some data for analysis (optional)
        if len(self.buffer) < 1000:  # Keep buffer small
            self.buffer.extend(input_data.tolist())

        # Send processed audio to output port (optional)
        self.output_port.get_array()[:] = processed_data

        # Print RMS level every 100 blocks (optional)
        if hasattr(self, 'block_counter'):
            self.block_counter += 1
        else:
            self.block_counter = 0

        if self.block_counter % 100 == 0:
            rms = np.sqrt(np.mean(input_data ** 2))
            if rms > 0.001:  # Only print if significant signal
                print(f"RMS Level: {rms:.4f}")

    def shutdown(self):
        print("JACK shutdown!")

    def start(self):
        """Activate the client"""
        with self.client:
            print(f"Audio receiver started. Sample rate: {self.sample_rate}, Block size: {self.blocksize}")
            print("Available ports:")
            print("Outputs:", self.client.get_ports(is_audio=True, is_output=True))
            print("Inputs:", self.client.get_ports(is_audio=True, is_input=True))

            try:
                input("Press Enter to quit...")
            except KeyboardInterrupt:
                pass
            print("Stopping audio receiver...")

def animate():
    graph_data = open('example.txt' , 'r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    for line in lines:
        if len(line) > 1:
            x,y = line.split(',')
            xs.append(float(x))
            ys.append(float(y))
    ax1.clear()
    ax1.plot(xs, ys)


if __name__ == "__main__":
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    interval = 1000

    #thread1 = threading.Thread(target=animation.FuncAnimation, args=(fig, animate,interval ), daemon=True)
    #plt.show()
    #thread1.start()


    receiver = AudioReceiver()
    receiver.start()


