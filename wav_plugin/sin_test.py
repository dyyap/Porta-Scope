import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
from scipy.io.wavfile import write


class SineWaveGenerator:
    def __init__(self, sample_rate=160000):  # 160kHz sample rate for high-quality 28kHz signal
        self.sample_rate = sample_rate

    def generate_wave(self, duration, center_freq, bandwidth, amplitude=0.5, smoothness=10):
        """
        Generate a sine wave with smooth frequency variation

        Parameters:
        - duration: Duration in seconds
        - center_freq: Center frequency in Hz
        - bandwidth: Bandwidth in Hz (frequency will vary ±bandwidth/2)
        - amplitude: Wave amplitude (0-1)
        - smoothness: Higher values = smoother frequency transitions (default 10)
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        # Frequency deviation is half the bandwidth
        freq_deviation = bandwidth / 2

        # Create much smoother frequency variation using a very low-frequency sine wave
        # Lower frequency = smoother transitions
        freq_variation_rate = 1 / smoothness  # Very slow variation for smoothness
        instantaneous_freq = center_freq + freq_deviation * np.sin(2 * np.pi * freq_variation_rate * t)

        # Generate the sine wave with varying frequency
        phase = 2 * np.pi * np.cumsum(instantaneous_freq) / self.sample_rate
        wave = amplitude * np.sin(phase)

        return t, wave, instantaneous_freq

    def generate_ultra_smooth_wave(self, duration, center_freq, bandwidth, amplitude=0.5):
        """
        Generate an ultra-smooth sine wave using Gaussian-modulated frequency variation
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        # Frequency deviation is half the bandwidth
        freq_deviation = bandwidth / 2

        # Create ultra-smooth frequency variation using multiple sine waves
        # Use harmonically related slow frequencies for very smooth transitions
        freq_var1 = 0.1 * np.sin(2 * np.pi * 0.05 * t)  # Very slow primary variation
        freq_var2 = 0.3 * np.sin(2 * np.pi * 0.02 * t)  # Even slower secondary variation
        freq_var3 = 0.2 * np.sin(2 * np.pi * 0.08 * t)  # Tertiary variation

        # Combine variations and apply Gaussian envelope for extra smoothness
        combined_variation = freq_var1 + freq_var2 + freq_var3

        # Apply a very gentle Gaussian envelope to make transitions even smoother
        envelope = np.exp(-((t - duration / 2) / (duration / 3)) ** 2)
        combined_variation *= envelope

        instantaneous_freq = center_freq + freq_deviation * combined_variation

        # Generate the sine wave with ultra-smooth frequency variations
        phase = 2 * np.pi * np.cumsum(instantaneous_freq) / self.sample_rate
        wave = amplitude * np.sin(phase)

        return t, wave, instantaneous_freq

    def generate_swept_wave(self, duration, center_freq, bandwidth, amplitude=0.5, sweep_type='linear'):
        """
        Generate a sine wave that sweeps through the bandwidth with smooth transitions
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        freq_start = center_freq - bandwidth / 2
        freq_end = center_freq + bandwidth / 2

        if sweep_type == 'linear':
            # Linear frequency sweep
            instantaneous_freq = freq_start + (freq_end - freq_start) * t / duration
        elif sweep_type == 'smooth':
            # Smooth S-curve sweep using tanh
            normalized_t = (t / duration - 0.5) * 6  # Scale for smooth transition
            smooth_factor = (np.tanh(normalized_t) + 1) / 2  # S-curve from 0 to 1
            instantaneous_freq = freq_start + (freq_end - freq_start) * smooth_factor
        elif sweep_type == 'cosine':
            # Cosine-based smooth sweep
            cosine_factor = (1 - np.cos(np.pi * t / duration)) / 2
            instantaneous_freq = freq_start + (freq_end - freq_start) * cosine_factor

        # Generate the sine wave
        phase = 2 * np.pi * np.cumsum(instantaneous_freq) / self.sample_rate
        wave = amplitude * np.sin(phase)

        return t, wave, instantaneous_freq

    def generate_clean_wave(self, duration, center_freq, amplitude=0.5):
        """
        Generate a perfectly clean sine wave at exactly the center frequency
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        # Pure sine wave at center frequency - perfectly smooth
        wave = amplitude * np.sin(2 * np.pi * center_freq * t)
        instantaneous_freq = np.full_like(t, center_freq)  # Constant frequency

        return t, wave, instantaneous_freq

    def generate_gaussian_smooth_wave(self, duration, center_freq, bandwidth, amplitude=0.5):
        """
        Generate a sine wave with Gaussian-smoothed random frequency variations
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        freq_deviation = bandwidth / 2

        # Create very smooth random variations using Gaussian filtering
        num_control_points = max(10, int(duration))  # Fewer control points = smoother
        control_times = np.linspace(0, duration, num_control_points)
        random_variations = np.random.uniform(-1, 1, num_control_points)

        # Apply Gaussian smoothing to the random variations
        try:
            from scipy import ndimage
            sigma = 2  # Smoothing parameter
            smoothed_variations = ndimage.gaussian_filter1d(random_variations, sigma)
        except ImportError:
            # Fallback if scipy not available - use simple moving average
            smoothed_variations = random_variations
            for _ in range(3):  # Multiple passes for smoothing
                smoothed_variations = np.convolve(smoothed_variations, [0.25, 0.5, 0.25], mode='same')

        # Interpolate to create ultra-smooth frequency variations
        freq_variations = np.interp(t, control_times, smoothed_variations)

        # Additional smoothing with a moving average
        window_size = int(self.sample_rate * 0.05)  # 50ms smoothing window
        if window_size > 1:
            freq_variations = np.convolve(freq_variations,
                                          np.ones(window_size) / window_size, mode='same')

        instantaneous_freq = center_freq + freq_deviation * freq_variations

        # Generate the sine wave
        phase = 2 * np.pi * np.cumsum(instantaneous_freq) / self.sample_rate
        wave = amplitude * np.sin(phase)

        return t, wave, instantaneous_freq

    def plot_wave(self, t, wave, instantaneous_freq, title="Sine Wave"):
        """Plot the waveform, frequency variation, and frequency spectrum"""
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))

        # Time domain plot - show more cycles for smoothness visualization
        plot_duration = min(0.001, len(t) / self.sample_rate)  # 1ms for high sample rate
        plot_samples = int(plot_duration * self.sample_rate)

        if plot_samples > 0:
            ax1.plot(t[:plot_samples] * 1000, wave[:plot_samples], linewidth=1.5)
            ax1.set_xlabel('Time (ms)')
            ax1.set_ylabel('Amplitude')
            ax1.set_title(f'{title} - Time Domain (first 1ms @ 160kHz)')
            ax1.grid(True, alpha=0.3)

        # Frequency variation plot with enhanced smoothness visualization
        ax2.plot(t, instantaneous_freq / 1000, linewidth=2, color='blue')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Frequency (kHz)')
        ax2.set_title(f'{title} - Frequency Variation (Smoothness @ 160kHz)')
        ax2.grid(True, alpha=0.3)

        # Add frequency range indicators
        center_f = np.mean(instantaneous_freq) / 1000
        min_f = np.min(instantaneous_freq) / 1000
        max_f = np.max(instantaneous_freq) / 1000
        ax2.axhline(y=center_f, color='red', linestyle='--', alpha=0.7, label=f'Center: {center_f:.1f}kHz')
        ax2.axhline(y=min_f, color='green', linestyle=':', alpha=0.7, label=f'Min: {min_f:.1f}kHz')
        ax2.axhline(y=max_f, color='green', linestyle=':', alpha=0.7, label=f'Max: {max_f:.1f}kHz')
        ax2.legend()

        # Frequency domain plot
        fft = np.fft.fft(wave)
        freqs = np.fft.fftfreq(len(fft), 1 / self.sample_rate)
        magnitude = np.abs(fft)

        # Plot only positive frequencies
        positive_freqs = freqs[:len(freqs) // 2] / 1000  # Convert to kHz
        positive_magnitude = magnitude[:len(magnitude) // 2]

        # Only plot significant magnitudes
        max_mag = np.max(positive_magnitude)
        mask = positive_magnitude > max_mag * 1e-4

        ax3.plot(positive_freqs[mask], 20 * np.log10(positive_magnitude[mask] + 1e-10),
                 linewidth=1.5, color='purple')
        ax3.set_xlabel('Frequency (kHz)')
        ax3.set_ylabel('Magnitude (dB)')
        ax3.set_title(f'{title} - Frequency Spectrum (160kHz sampling)')
        ax3.grid(True, alpha=0.3)

        # Set frequency plot limits
        center_freq_khz = np.mean(instantaneous_freq) / 1000
        ax3.set_xlim(max(0, center_freq_khz - 5), center_freq_khz + 5)

        # Add sample rate info
        fig.suptitle(f'Sample Rate: {self.sample_rate / 1000:.0f}kHz | Nyquist: {self.sample_rate / 2000:.0f}kHz',
                     fontsize=10, y=0.02)

        plt.tight_layout()
        plt.show()

    def play_wave(self, wave):
        """Play the generated wave"""
        try:
            print(f"Note: 28kHz is above human hearing range (~20kHz max)")
            print(f"Playing at {self.sample_rate / 1000:.0f}kHz sample rate...")
            sd.play(wave, self.sample_rate)
            sd.wait()
        except Exception as e:
            print(f"Audio playback error: {e}")
            print("Note: Your audio device may not support 160kHz playback")

    def save_wave(self, wave, filename="smooth_sine_28khz_160k.wav"):
        """Save the wave to a WAV file at 160kHz"""
        wave_normalized = np.int16(wave * 32767)
        write(filename, self.sample_rate, wave_normalized)
        print(f"Smooth wave saved as {filename} @ {self.sample_rate / 1000:.0f}kHz")


# Example with ultra-smooth 28kHz waves at 160kHz sample rate
def example_waves():
    """Generate ultra-smooth 28kHz sine wave examples with 3kHz bandwidth at 160kHz"""
    generator = SineWaveGenerator()

    print("=" * 70)
    print("ULTRA-SMOOTH 28kHz SINE WAVE GENERATOR")
    print(f"Sample Rate: {generator.sample_rate / 1000:.0f}kHz ({generator.sample_rate:,} samples/sec)")
    print(f"Nyquist Frequency: {generator.sample_rate / 2000:.0f}kHz")
    print("Target: 28kHz ± 1.5kHz (26.5-29.5kHz range)")
    print("=" * 70)

    # Parameters for 28kHz with 3kHz bandwidth
    params = {
        "duration": 5,  # Longer duration to see smoothness
        "center_freq": 28000,
        "bandwidth": 3000,
        "amplitude": 0.7
    }

    print(f"\nGeneration Parameters:")
    print(f"  Duration: {params['duration']} seconds")
    print(f"  Center Frequency: {params['center_freq']:,} Hz ({params['center_freq'] / 1000:.1f} kHz)")
    print(f"  Bandwidth: {params['bandwidth']:,} Hz ({params['bandwidth'] / 1000:.1f} kHz)")
    print(
        f"  Frequency Range: {(params['center_freq'] - params['bandwidth'] / 2) / 1000:.1f} - {(params['center_freq'] + params['bandwidth'] / 2) / 1000:.1f} kHz")
    print(f"  Amplitude: {params['amplitude']}")
    print(f"  Total Samples: {int(params['duration'] * generator.sample_rate):,}")

    # Generate ultra-smooth examples
    examples = [
        ("Ultra-Clean 28kHz Sine", generator.generate_clean_wave,
         {"duration": params["duration"], "center_freq": params["center_freq"], "amplitude": params["amplitude"]}),

        ("Ultra-Smooth Multi-Harmonic", generator.generate_ultra_smooth_wave, params),

        ("Super-Smooth Basic (50x)", generator.generate_wave,
         {**params, "smoothness": 50}),  # Very high smoothness

        ("Super-Smooth Basic (100x)", generator.generate_wave,
         {**params, "smoothness": 100}),  # Ultra high smoothness

        ("Smooth Cosine Sweep", generator.generate_swept_wave,
         {**params, "sweep_type": "cosine"}),

        ("Smooth S-Curve Sweep", generator.generate_swept_wave,
         {**params, "sweep_type": "smooth"}),

        ("Gaussian-Smoothed Random", generator.generate_gaussian_smooth_wave, params),
    ]

    for i, (type_name, method, method_params) in enumerate(examples, 1):
        print(f"\n[{i}/{len(examples)}] Generating: {type_name}")
        print("-" * 50)

        # Generate the wave
        t, wave, freq = method(**method_params)

        title = f"{type_name} - 28kHz @ 160kHz"
        if "bandwidth" in method_params and method_params.get("bandwidth", 0) > 0:
            title += f" ± {method_params['bandwidth'] / 2000:.1f}kHz"

        # Plot the wave
        generator.plot_wave(t, wave, freq, title)

        # Calculate detailed statistics
        freq_diff = np.diff(freq)


if __name__ == "__main__":
    # Install required packages if not already installed:
    # pip install numpy matplotlib sounddevice scipy

    print("28kHz Sine Wave Generator")
    print("Sample rate: 96kHz (suitable for 28kHz signals)")
    print("=" * 50)
    print("Choose an option:")
    print("1. Interactive wave generator")
    print("2. Show 28kHz examples with 3kHz bandwidth")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        interactive_wave_generator()
    elif choice == "2":
        example_waves()
    else:
        print("Invalid choice. Running 28kHz examples...")
        example_waves()