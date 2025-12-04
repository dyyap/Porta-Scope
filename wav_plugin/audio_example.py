import numpy as np
import pyaudio
import threading


class SineWaveGenerator:
    def __init__(self, frequency=440, sample_rate=44100, amplitude=0.3):
        self.frequency = frequency
        self.sample_rate = sample_rate
        self.amplitude = amplitude
        self.is_playing = False
        self.phase = 0

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None

        # Initialize Reading


    def callback(self, in_data, frame_count, time_info, status):
        # Generate sine wave samples
        samples = np.arange(frame_count) + self.phase
        sine_wave = self.amplitude * np.sin(2 * np.pi * self.frequency * samples / self.sample_rate)

        # Update phase for continuity
        self.phase += frame_count

        # Convert to bytes
        output = sine_wave.astype(np.float32).tobytes()
        return output, pyaudio.paContinue

    def data(self):
       raw_audio_data = self.stream(2014)
       audio_array = np.frombuffer(raw_audio_data, dtype=np.int32)
       return audio_array

    def start(self):
        if not self.is_playing:
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=1024,
                stream_callback=self.callback
            )
            self.is_playing = True
            self.stream.start_stream()

    def stop(self):
        if self.is_playing:
            self.stream.stop_stream()
            self.stream.close()
            self.is_playing = False

    def set_frequency(self, frequency):
        self.frequency = frequency

    def set_amplitude(self, amplitude):
        self.amplitude = max(0, min(1, amplitude))  # Clamp between 0 and 1

    def __del__(self):
        if hasattr(self, 'p'):
            self.p.terminate()


# Example usage
if __name__ == "__main__":
    import time

    # Create generator
    generator = SineWaveGenerator(frequency=440, amplitude=0.3)  # A4 note


    try:
        print(generator.data())
        generator.start()
        raw_audio_data = generator.data()
        print(raw_audio_data)
        print("Playing 440 Hz sine wave...")
        time.sleep(2)

        # Change frequency
        generator.set_frequency(880)  # A5 note
        print("Changed to 880 Hz...")
        time.sleep(2)

        generator.stop()
        print("Stopped")
    except KeyboardInterrupt:
        generator.stop()