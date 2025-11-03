import numpy as np
import matplotlib.pyplot as plt


def sin(amplitude, frequency, sampling_rate, duration):

    # Time array
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    # Generate sine wave
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)

    # Plotting
    plt.figure(figsize=(10, 4))
    plt.plot(t, sine_wave)
    plt.title('Sine Wave')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()

def square(amplitude, frequency, sampling_rate, duration):

    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    # Generate square wave
    square_wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))

    # Plotting
    plt.figure(figsize=(10, 4))
    plt.plot(t, square_wave)
    plt.title('Square Wave')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()

def triangle(amplitude, frequency, sampling_rate, duration):
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    # Generate triangle wave
    triangle_wave = amplitude * (2 * np.abs(2 * frequency * t - np.floor(0.5 + 2 * frequency * t)) - 1)

    # Plotting
    plt.figure(figsize=(10, 4))
    plt.plot(t, triangle_wave)
    plt.title('Triangle Wave')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()

def Saw(amplitude, frequency, sampling_rate, duration):
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    # Generate sawtooth wave
    sawtooth_wave = amplitude * (2 * (frequency * t - np.floor(0.5 + frequency * t)))

    # Plotting
    plt.figure(figsize=(10, 4))
    plt.plot(t, sawtooth_wave)
    plt.title('Sawtooth Wave')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()


# Parameters (same as sine wave)
amplitude = 1.0
frequency = 2.0
sampling_rate = 1000
duration = 1.0

sin(amplitude, frequency, sampling_rate, duration)