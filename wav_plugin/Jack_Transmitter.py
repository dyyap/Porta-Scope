import jack
import numpy as np
import threading
import time


class AudioSender:
    def __init__(self, client_name="audio_sender"):
        self.client = jack.Client(client_name)
        self.sample_rate = self.client.samplerate
        self.blocksize = self.client.blocksize

        # Create output port
        self.output_port = self.client.outports.register('output')

        # Sine wave parameters
        self.frequency = 440.0  # A4 note
        self.phase = 0.0
        self.amplitude = 0.3

        # Set the process callback
        self.client.set_process_callback(self.process_audio)

        # Set shutdown callback
        self.client.set_shutdown_callback(self.shutdown)

    def process_audio(self, frames):
        """Generate and send audio data"""
        # Generate sine wave
        samples = np.arange(frames) + self.phase
        audio_data = self.amplitude * np.sin(2 * np.pi * self.frequency * samples / self.sample_rate)

        # Update phase for next block
        self.phase += frames

        # Send audio to output port
        self.output_port.get_array()[:] = audio_data.astype(np.float32)

    def shutdown(self):
        print("JACK shutdown!")

    def start(self):
        """Activate the client"""
        with self.client:
            print(f"Audio sender started. Sample rate: {self.sample_rate}, Block size: {self.blocksize}")
            print("Available ports:")
            print("Outputs:", self.client.get_ports(is_audio=True, is_output=True))
            print("Inputs:", self.client.get_ports(is_audio=True, is_input=True))

            try:
                self.client.connect(self.output_port, 'audio_receiver:input')
                input("Press Enter to quit...")
            except KeyboardInterrupt:
                pass
            print("Stopping audio sender...")


if __name__ == "__main__":
    sender = AudioSender()
    sender.start()