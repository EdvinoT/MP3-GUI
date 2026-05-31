import wave
import math
import struct
import os

def generate_premium_ui_sound(filename, base_freq, duration_ms, volume=0.5, type="click"):
    sample_rate = 44100
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    
    # Ensure directory exists if there is a path specified
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            progress = i / num_samples
            
            if type == "click":
                # --- SERIOUS MECHANICAL CLICK ---
                # Rapid downwards pitch bend simulates physical depth/mass
                current_freq = base_freq * math.exp(-progress * 4.5)
                
                # Base fundamental tone
                angle = 2.0 * math.pi * current_freq * t
                fundamental = math.sin(angle)
                
                # Add a crisp harmonic overtone (gives it a high-end glass/metal edge)
                overtone_angle = 2.0 * math.pi * (current_freq * 2.8) * t
                overtone = math.sin(overtone_angle) * 0.3
                
                sample = fundamental + overtone
                
                # Sharp organic acoustic dropoff curve
                decay = math.exp(-t * 65)
                
            else:
                # --- MATTE MICRO-SCROLL BLIP ---
                # Ultra-short pitch drop (simulates a subtle mechanical wheel detent)
                current_freq = base_freq * math.exp(-progress * 3.0)
                
                angle = 2.0 * math.pi * current_freq * t
                fundamental = math.sin(angle)
                
                # Blend a tiny amount of high-frequency white noise for texturing
                noise = (int(i * 1234567) % 200 - 100) / 100.0
                sample = (fundamental * 0.85) + (noise * 0.15)
                
                # Extreme immediate dampening so it doesn't ring out
                decay = math.exp(-t * 220)
                
            # Soft-clip limiter to prevent digital distortion popping
            final_wave = sample * volume * decay
            final_wave = max(-1.0, min(1.0, final_wave))
            
            # Pack into standard 16-bit binary PCM
            packed_sample = struct.pack('<h', int(final_wave * 32767))
            wav_file.writeframesraw(packed_sample)

print("Synthesizing premium, serious interface audio assets...")

# Create click.wav: Starts at 650Hz and drops down rapidly over 50ms (Deep, premium feel)
generate_premium_ui_sound("click.wav", base_freq=650, duration_ms=50, volume=0.5, type="click")

# Create scroll.wav: Starts at 1200Hz and drops instantly over 12ms (Subtle tactile click)
generate_premium_ui_sound("scroll.wav", base_freq=1200, duration_ms=12, volume=0.2, type="scroll")

print("Successfully generated professional 'click.wav' and 'scroll.wav'!")