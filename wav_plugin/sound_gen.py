import math
import wave
import struct
import numpy as np
import matplotlib.pyplot as plt

audio = []
# Parameters (same as sine wave)
amplitude = 100.0
sampling_rate = 160000
duration = 1.0



def append_silence(duration_mil=5000):
    #adding silence is just adding samples
    num_samples = duration_mil * (sampling_rate / 1000)

    for i in range(int(num_samples)):
        audio.append(0.0)

    return

def append_sinewave(
        #defaults
        freq=440.0,
        duration_milliseconds=500,
        volume=1.0):
    """
    The sine wave generated here is the standard beep.  If you want something
    more aggresive you could try a square or saw tooth waveform.   Though there
    are some rather complicated issues with making high quality square and
    sawtooth waves... which we won't address here :)
    """

    t = np.linspace(0, duration_milliseconds, int(sampling_rate * duration_milliseconds), endpoint=False)
    global audio # using global variables isn't cool.
    num_samples = duration_milliseconds * (sampling_rate / 1000.0)
    sine_wave = volume * amplitude * np.sin(2 * np.pi * freq * t)
    for x in range(len(sine_wave)):
        audio.append(sine_wave[x])
    return t

def append_square(
        #defaults
        freq=440.0,
        duration_milliseconds=500,
        volume=1.0):
    """
    The sine wave generated here is the standard beep.  If you want something
    more aggresive you could try a square or saw tooth waveform.   Though there
    are some rather complicated issues with making high quality square and
    sawtooth waves... which we won't address here :)
    """

    global audio # using global variables isn't cool.
    num_samples = duration_milliseconds * (sampling_rate / 1000.0)
    for x in range(int(num_samples)):
        audio.append(volume * amplitude * np.sign(np.sin(2 * np.pi * freq * x/sampling_rate)))
    return

def append_triangle(
        #defaults
        freq=440.0,
        duration_milliseconds=500,
        volume=1.0):
    """
    The sine wave generated here is the standard beep.  If you want something
    more aggresive you could try a square or saw tooth waveform.   Though there
    are some rather complicated issues with making high quality square and
    sawtooth waves... which we won't address here :)
    """
    t = np.linspace(0, duration_milliseconds, int(sampling_rate * duration_milliseconds), endpoint=False)
    global audio # using global variables isn't cool.
    num_samples = duration_milliseconds * (sampling_rate / 1000.0)
    triangle_wave = amplitude * (2 * np.abs(2 * freq* t - np.floor(0.5 + 2 * freq * t)) - 1)
    for x in range(len(triangle_wave)):
        audio.append(triangle_wave[x])
    return

def append_saw(
        #defaults
        freq=440.0,
        duration_milliseconds=500,
        volume=1.0):
    """
    The sine wave generated here is the standard beep.  If you want something
    more aggresive you could try a square or saw tooth waveform.   Though there
    are some rather complicated issues with making high quality square and
    sawtooth waves... which we won't address here :)
    """

    global audio # using global variables isn't cool.
    num_samples = duration_milliseconds * (sampling_rate / 1000.0)
    for x in range(int(num_samples)):
        audio.append(volume * amplitude * (2 * (freq * x/sampling_rate - np.floor(0.5 + freq * x/sampling_rate))))
    return




def save_wav(file_name):
    # Open up a wav file
    wav_file=wave.open(file_name,"w")
    # wav params
    nchannels = 1
    sampwidth = 2

    # 44100 is the industry standard sample rate - CD quality.  If you need to
    # save on file size you can adjust it downwards. The stanard for low quality
    # is 8000 or 8kHz.

    nframes = len(audio)
    print(nframes)
    comptype = "NONE"
    compname = "not compressed"
    wav_file.setparams((nchannels, sampwidth, sampling_rate, nframes, comptype, compname))

    # WAV files here are using short, 16 bit, signed integers for the
    # sample size.  So we multiply the floating point data we have by 32767, the
    # maximum value for a short integer.  NOTE: It is theortically possible to
    # use the floating point -1.0 to 1.0 data directly in a WAV file but not
    # obvious how to do that using the wave module in python.
    for sample in audio:
        wav_file.writeframes(sample)
    wav_file.close()

    return

print("SINE_WAV")
x = append_sinewave(28000, 5, 1)
#print("TRIANGLE_WAV")
#append_triangle(3000, 1000, 1)
save_wav("output.wav")

global_sampling_rate = 160000
total_duration = 1
amplitude_max = np.iinfo(np.int16).max

# Plotting
plt.figure(figsize=(10, 4))
plt.plot(x, audio)
plt.title('Triangle Wave')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
#plt.ylim(-2000, 2000)
plt.grid(True)
plt.show()