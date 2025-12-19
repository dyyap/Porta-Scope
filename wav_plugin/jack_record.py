#!/usr/bin/env python3
"""
JACK Audio Sink - Records audio from JACK and saves to WAV files
"""

import jack
import soundfile as sf
import numpy as np
import threading
import queue
import datetime
import os
import argparse
import signal
import sys


class JackAudioSink:
    def __init__(self, client_name="audio_recorder", channels=2, auto_connect=True):
        """
        Initialize JACK audio sink

        Args:
            client_name: Name for the JACK client
            channels: Number of input channels (1=mono, 2=stereo)
            auto_connect: Automatically connect to system playback ports
        """
        self.client_name = client_name
        self.channels = channels
        self.auto_connect = auto_connect

        # Audio buffer and recording state
        self.audio_queue = queue.Queue(maxsize=100)  # Limit queue size
        self.is_recording = False
        self.output_file = None
        self.sample_rate = None

        # Threading
        self.write_thread = None
        self.should_stop = threading.Event()

        # Initialize JACK client
        self.client = jack.Client(client_name)
        self.sample_rate = self.client.samplerate

        # Create input ports
        self.input_ports = []
        for i in range(channels):
            port_name = f"input_{i + 1}" if channels > 1 else "input"
            self.input_ports.append(
                self.client.inports.register(port_name)
            )

        # Set JACK callbacks
        self.client.set_process_callback(self.process_callback)
        self.client.set_shutdown_callback(self.shutdown_callback)

        print(f"JACK client '{client_name}' initialized")
        print(f"Sample rate: {self.sample_rate} Hz")
        print(f"Channels: {channels}")

    def process_callback(self, frames):
        """JACK process callback - called for each audio block"""
        if not self.is_recording:
            return

        try:
            # Read audio data from input ports
            if self.channels == 1:
                audio_data = self.input_ports[0].get_array()
            else:
                # Interleave multi-channel audio
                audio_data = np.column_stack([
                    port.get_array() for port in self.input_ports
                ])

            # Add to queue for writing (non-blocking)
            self.audio_queue.put(audio_data.copy(), block=False)

        except queue.Full:
            print("Warning: Audio buffer full, dropping frames")
        except Exception as e:
            print(f"Error in process callback: {e}")

    def shutdown_callback(self, status, reason):
        """Called when JACK server shuts down"""
        print(f"JACK shutdown: {reason}")
        self.stop_recording()

    def start_jack(self):
        """Activate JACK client and optionally auto-connect"""
        self.client.activate()

        if self.auto_connect:
            self.auto_connect_ports()

        print("JACK client activated")

    def auto_connect_ports(self):
        """Auto-connect to system capture ports"""
        try:
            capture_ports = self.client.get_ports(
                is_physical=True, is_output=True, is_audio=True
            )

            for i, input_port in enumerate(self.input_ports):
                if i < len(capture_ports):
                    self.client.connect(capture_ports[i], input_port)
                    print(f"Connected {capture_ports[i].name} -> {input_port.name}")

        except Exception as e:
            print(f"Auto-connect failed: {e}")
            print("You may need to connect ports manually")

    def start_recording(self, filename=None):
        """Start recording audio to file"""
        if self.is_recording:
            print("Already recording!")
            return False

        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

        try:
            self.output_file = sf.SoundFile(
                filename,
                mode='w',
                samplerate=self.sample_rate,
                channels=self.channels,
                format='WAV',
                subtype='PCM_24'  # 24-bit PCM
            )

            # Clear any old data and reset stop event
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break

            self.should_stop.clear()

            # Start writer thread
            self.write_thread = threading.Thread(target=self.write_worker)
            self.write_thread.start()

            self.is_recording = True
            print(f"Started recording to: {filename}")
            return True

        except Exception as e:
            print(f"Failed to start recording: {e}")
            return False

    def stop_recording(self):
        """Stop recording"""
        if not self.is_recording:
            return

        print("Stopping recording...")
        self.is_recording = False
        self.should_stop.set()

        # Wait for writer thread to finish
        if self.write_thread and self.write_thread.is_alive():
            self.write_thread.join(timeout=5.0)

        # Close output file
        if self.output_file:
            try:
                self.output_file.close()
                print(f"Recording saved: {self.output_file.name}")
            except Exception as e:
                print(f"Error closing file: {e}")
            finally:
                self.output_file = None

    def write_worker(self):
        """Background thread for writing audio data to file"""
        while not self.should_stop.is_set() or not self.audio_queue.empty():
            try:
                # Get audio data with timeout
                audio_data = self.audio_queue.get(timeout=0.1)

                # Write to file
                if self.output_file:
                    self.output_file.write(audio_data)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error writing audio: {e}")
                break

    def list_ports(self):
        """List available JACK ports"""
        print("\nAvailable JACK ports:")

        # Input ports (capture)
        capture_ports = self.client.get_ports(is_output=True, is_audio=True)
        print("\nCapture ports (sources):")
        for port in capture_ports:
            print(f"  {port.name}")

        # Output ports (playback)
        playback_ports = self.client.get_ports(is_input=True, is_audio=True)
        print("\nPlayback ports (destinations):")
        for port in playback_ports:
            print(f"  {port.name}")

    def get_connections(self):
        """Show current port connections"""
        print(f"\nConnections for {self.client_name}:")
        for i, port in enumerate(self.input_ports):
            connections = self.client.get_all_connections(port)
            print(f"  {port.name}: {[conn.name for conn in connections]}")

    def cleanup(self):
        """Clean shutdown"""
        self.stop_recording()
        if hasattr(self, 'client') and self.client:
            self.client.deactivate()
            self.client.close()
        print("Cleanup complete")


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\nReceived interrupt signal...")
    global recorder
    if recorder:
        recorder.cleanup()
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="JACK Audio Recorder")
    parser.add_argument('-c', '--channels', type=int, default=2, choices=[1, 2],
                        help='Number of channels (1=mono, 2=stereo)')
    parser.add_argument('-n', '--name', default='audio_recorder',
                        help='JACK client name')
    parser.add_argument('-o', '--output',
                        help='Output filename (default: auto-generated)')
    parser.add_argument('--no-autoconnect', action='store_true',
                        help='Disable automatic port connection')
    parser.add_argument('--list-ports', action='store_true',
                        help='List available ports and exit')

    args = parser.parse_args()

    global recorder
    recorder = None

    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Create recorder
        recorder = JackAudioSink(
            client_name=args.name,
            channels=args.channels,
            auto_connect=not args.no_autoconnect
        )

        # Start JACK
        recorder.start_jack()

        # List ports if requested
        if args.list_ports:
            recorder.list_ports()
            return

        # Show initial connections
        recorder.get_connections()

        print("\nCommands:")
        print("  [Enter] - Start/stop recording")
        print("  'l' - List ports")
        print("  'c' - Show connections")
        print("  'q' - Quit")

        # Main loop
        while True:
            try:
                cmd = input("\n> ").strip().lower()

                if cmd == 'q' or cmd == 'quit':
                    break
                elif cmd == 'l':
                    recorder.list_ports()
                elif cmd == 'c':
                    recorder.get_connections()
                elif cmd == '' or cmd == 'r':
                    if recorder.is_recording:
                        recorder.stop_recording()
                    else:
                        recorder.start_recording(args.output)
                else:
                    print("Unknown command")

            except EOFError:
                break

    except jack.JackOpenError:
        print("Error: Could not connect to JACK server")
        print("Make sure JACK is running")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        if recorder:
            recorder.cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())