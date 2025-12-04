import wave, struct

wavefile = wave.open('sine.wav', 'r')

length = wavefile.getnframes() # Gets the wav file in frames
for i in range(0, length):
    wavedata = wavefile.readframes(1) #read x frames at a time
    data = struct.unpack("<h", wavedata) #Gets the struct
    print(int(data[0]))
