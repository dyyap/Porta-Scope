import matplotlib.pyplot as plt
import matplotlib.animation as animation
from jinja2.compiler import generate
from matplotlib import style
import numpy as np

class SineWaveData:
    def __init__(self, sample_rate=1000):
        self.sample_rate = sample_rate

    def generate(self, frequency, amplitude=1, duration=1, phase=0):
        """Generate sine wave data"""
        num_samples = int(self.sample_rate * duration)
        t = np.arange(num_samples) / self.sample_rate
        return amplitude * np.sin(2 * np.pi * frequency * t + phase)

    def generate_multiple_frequencies(self, frequencies, amplitudes=None, duration=1):
        """Generate multiple sine wave data"""
        if amplitudes is None:
            aplitudes = [1] * len(frequencies)

        result = np.zeros(int(self.sample_rate * duration))
        for freq, amp in zip(frequencies, amplitudes):
            result += self.generate(freq, amp, duration)

        return result


style.use("fivethirtyeight")
cache_frame_data=False

'''
example usage

'''

generator = SineWaveData(sample_rate = 44100)

wave_440hz = generator.generate(frequency = 440, duration=1)

print(wave_440hz)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
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

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
