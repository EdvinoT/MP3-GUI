# download_sound_assets.py
import wave
import math
import struct
import os

def generate_premium_ui_assets(filename, duration_ms, volume=0.5, type="slash"):
    sample_rate = 44100
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            progress = i / num_samples
            
            # High-fidelity white noise generation for organic friction textures
            raw_noise = (int(i * 1234567) % 200 - 100) / 100.0
            
            if type == "slash":
                # --- SERIOUS METALLIC SLASH CLICK ---
                # Rapid low-mid body drop from 380Hz to 60Hz
                freq = 380 * math.exp(-progress * 6.0)
                angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(angle)
                
                # High-passed air burst creates a razor-sharp mechanical slice texture
                noise_envelope = math.cos(progress * (math.pi / 2))
                textured_noise = raw_noise * noise_envelope * 0.75
                
                # Blend the elements (Heavy physical punch + metallic friction air)
                sample = (fundamental * 0.35) + (textured_noise * 0.65)
                decay = math.exp(-t * 28)  # Lets the tail whisper off elegantly
                
            else:
                # --- TACTILE NOTCH SCROLL TICK ---
                # Fixed deep 180Hz mechanical tone for a weighted, serious feel
                freq = 180 
                angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(angle)
                
                # Crisp transient pop in the first 4 milliseconds mimics physical contact
                snap = raw_noise * 0.45 if i < (sample_rate * 0.004) else 0.0
                
                sample = (fundamental * 0.65) + snap
                decay = math.exp(-t * 95)  # Fast, sharp mechanical clamp
                
            # Master clipping protection
            final_wave = sample * volume * decay
            final_wave = max(-1.0, min(1.0, final_wave))
            
            # Convert float sample to 16-bit PCM binary data
            packed_sample = struct.pack('<h', int(final_wave * 32767))
            wav_file.writeframesraw(packed_sample)

print("Locally compounding professional audio assets (bypassing networks)...")

# Generate click.wav (140ms dramatic mechanical slice click)
generate_premium_ui_assets("click.wav", duration_ms=140, volume=0.7, type="slash")

# Generate scroll.wav (45ms explicit heavy gear detent tick)
generate_premium_ui_assets("scroll.wav", duration_ms=45, volume=0.4, type="scroll")

print("Successfully written 'click.wav' and 'scroll.wav' locally!")