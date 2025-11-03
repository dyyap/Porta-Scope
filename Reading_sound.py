import wave, struct

wavefile = wave.open('sine.wav', 'r')

length = wavefile.getnframes()
for i in range(0, length):
    wavedata = wavefile.readframes(1)
    data = struct.unpack("<h", wavedata)
    print(int(data[0]))

wavedata = wavefile.readframes(13)
data = struct.unpack("<13h", wavedata)