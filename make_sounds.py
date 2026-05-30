import wave
import math
import struct

def generate_synth_sound(filename, frequency, duration_ms, volume=0.5, type="click"):
    sample_rate = 44100
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    
    with wave.open(filename, 'w') as wav_file:
        # Set channels (1 = mono), sample width (2 bytes = 16-bit), and framerate
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            
            # Create a professional audio decay envelope so it doesn't pop roughly
            decay = math.exp(-t * (50 if type == "click" else 120))
            
            # Synthesize the wave shape
            if type == "click":
                # A snappy, subtle low-to-high frequency chime sweep
                freq = frequency + (i * 0.5)
                angle = 2.0 * math.pi * freq * t
                sample = math.sin(angle)
            else:
                # A very rapid, minimal wooden/percussive tick for scrolling
                angle = 2.0 * math.pi * frequency * t
                sample = math.sin(angle) * (1.0 if (i % 2 == 0) else -1.0) # Add slight noise texture
                
            # Finalize amplitude math normalization bounds
            packed_sample = struct.pack('<h', int(sample * volume * decay * 32767))
            wav_file.writeframesraw(packed_sample)

print("Synthesizing premium interface audio assets...")
# Create click.wav: 1000Hz tone lasting 80 milliseconds (Snappy & Clean)
generate_synth_sound("click.wav", frequency=1000, duration_ms=80, volume=0.4, type="click")

# Create scroll.wav: 1800Hz tone lasting 15 milliseconds (Short, micro-percussive blip)
generate_synth_sound("scroll.wav", frequency=1800, duration_ms=15, volume=0.2, type="tick")
print("Successfully generated 'click.wav' and 'scroll.wav' inside your project root directory!")