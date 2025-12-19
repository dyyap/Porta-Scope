import jack
import soundfile as sf
import threading
import time
import sys
import argparse


class JackWavPlayer:
    def __init__(self, wav_file):
        self.wav_file = wav_file
        self.audio_data = None
        self.sample_rate = None
        self.channels = None
        self.position = 0
        self.playing = False
        self.client = None

        # Load the WAV file
        self.load_wav()

        # Create JACK client
        self.client = jack.Client("WavPlayer")

        # Register output ports based on number of channels
        self.output_ports = []
        for i in range(self.channels):
            port = self.client.outports.register(f'out_{i + 1}')
            self.output_ports.append(port)

        # Set process callback
        self.client.set_process_callback(self.process_callback)

        # Set shutdown callback
        self.client.set_shutdown_callback(self.shutdown_callback)

    def load_wav(self):
        """Load the WAV file using soundfile"""
        try:
            self.audio_data, self.sample_rate = sf.read(self.wav_file, dtype='float32')

            # Handle mono vs stereo
            if len(self.audio_data.shape) == 1:
                self.channels = 1
                self.audio_data = self.audio_data.reshape(-1, 1)
            else:
                self.channels = self.audio_data.shape[1]

            print(f"Loaded: {self.wav_file}")
            print(f"Sample rate: {self.sample_rate} Hz")
            print(f"Channels: {self.channels}")
            print(f"Duration: {len(self.audio_data) / self.sample_rate:.2f} seconds")

        except Exception as e:
            print(f"Error loading WAV file: {e}")
            sys.exit(1)

    def process_callback(self, frames):
        """JACK process callback - called for each audio block"""
        if not self.playing:
            # Output silence when not playing
            for port in self.output_ports:
                port.get_array().fill(0)
            return

        # Calculate how many frames we can actually play
        frames_available = len(self.audio_data) - self.position
        frames_to_play = min(frames, frames_available)

        # Copy audio data to output ports
        for ch, port in enumerate(self.output_ports):
            output_buffer = port.get_array()

            if frames_to_play > 0:
                # Copy audio data
                if ch < self.channels:
                    output_buffer[:frames_to_play] = self.audio_data[
                        self.position:self.position + frames_to_play, ch
                    ]
                else:
                    # If we have more output ports than channels, duplicate the last channel
                    output_buffer[:frames_to_play] = self.audio_data[
                        self.position:self.position + frames_to_play, -1
                    ]

                # Fill remaining frames with silence if needed
                if frames_to_play < frames:
                    output_buffer[frames_to_play:].fill(0)
            else:
                # No more audio data, fill with silence
                output_buffer.fill(0)

        # Update position
        self.position += frames_to_play

        # Stop playing if we've reached the end
        if self.position >= len(self.audio_data):
            self.playing = False
            print("Playback finished")

    def shutdown_callback(self):
        """Called when JACK shuts down"""
        print("JACK shutdown")
        self.playing = False

    def start_jack(self):
        """Start the JACK client"""
        try:
            self.client.activate()
            print(f"JACK client activated with sample rate: {self.client.samplerate}")

            # Check if sample rates match
            if self.client.samplerate != self.sample_rate:
                print(f"Warning: JACK sample rate ({self.client.samplerate}) "
                      f"doesn't match file sample rate ({self.sample_rate})")

            return True
        except Exception as e:
            print(f"Error starting JACK client: {e}")
            return False

    def play(self):
        """Start playback"""
        self.position = 0
        self.playing = True
        print("Starting playback...")

    def stop(self):
        """Stop playback"""
        self.playing = False
        print("Stopping playback...")

    def pause(self):
        """Pause playback"""
        self.playing = False
        print("Pausing playback...")

    def resume(self):
        """Resume playback"""
        self.playing = True
        print("Resuming playback...")

    def is_playing(self):
        """Check if currently playing"""
        return self.playing and self.position < len(self.audio_data)

    def get_position(self):
        """Get current playback position in seconds"""
        return self.position / self.sample_rate if self.sample_rate else 0

    def cleanup(self):
        """Clean up resources"""
        if self.client:
            self.client.deactivate()
            self.client.close()


def main():
    parser = argparse.ArgumentParser(description='JACK WAV Player')
    parser.add_argument('wav_file', help='WAV file to play')
    parser.add_argument('--auto-connect', action='store_true',
                        help='Auto-connect to system playback ports')

    args = parser.parse_args()

    # Create player
    player = JackWavPlayer(args.wav_file)

    # Start JACK
    if not player.start_jack():
        return

    # Auto-connect to system ports if requested
    if args.auto_connect:
        try:
            # Get system playback ports
            system_ports = player.client.get_ports(
                is_physical=True, is_input=True, is_audio=True
            )

            # Connect our outputs to system inputs
            for i, output_port in enumerate(player.output_ports):
                if i < len(system_ports):
                    player.client.connect(output_port, system_ports[i])
                    print(f"Connected {output_port.name} to {system_ports[i].name}")
        except Exception as e:
            print(f"Auto-connection failed: {e}")
            print("You'll need to connect ports manually using a JACK connection manager")

    try:
        print("\nControls:")
        print("  p - play")
        print("  s - stop")
        print("  space - pause/resume")
        print("  q - quit")
        print("  i - show info")

        # Start playback
        player.play()

        # Simple command interface
        while True:
            try:
                cmd = input().strip().lower()

                if cmd == 'p':
                    player.play()
                elif cmd == 's':
                    player.stop()
                elif cmd == ' ' or cmd == 'pause':
                    if player.playing:
                        player.pause()
                    else:
                        player.resume()
                elif cmd == 'q' or cmd == 'quit':
                    break
                elif cmd == 'i' or cmd == 'info':
                    pos = player.get_position()
                    duration = len(player.audio_data) / player.sample_rate
                    status = "Playing" if player.is_playing() else "Stopped"
                    print(f"Status: {status} | Position: {pos:.2f}s / {duration:.2f}s")

            except (EOFError, KeyboardInterrupt):
                break

    finally:
        print("\nShutting down...")
        player.cleanup()


if __name__ == "__main__":
    main()