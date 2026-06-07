import wave
import struct
import random
import os

os.makedirs('assets/audio', exist_ok=True)

def generate_pew():
    with wave.open('assets/audio/shoot.wav', 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        # pitch drop for a 'pew' sound
        for i in range(int(44100 * 0.1)):
            freq = 1500 - (i / (44100 * 0.1)) * 1000
            if freq <= 0: freq = 1
            val = int((i % (44100/freq)) / (44100/freq) * 32767 * (1 - i/(44100*0.1)) * 0.3)
            w.writeframesraw(struct.pack('<h', val))

def generate_hit():
    with wave.open('assets/audio/hit.wav', 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        # white noise drop for a 'thud' sound
        for i in range(int(44100 * 0.15)):
            val = int(random.uniform(-32767, 32767) * (1 - i/(44100*0.15)) * 0.3)
            w.writeframesraw(struct.pack('<h', val))

generate_pew()
generate_hit()
print("Audio generated successfully!")