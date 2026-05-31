# download_sound_assets.py
import wave
import math
import struct

def generate_premium_ui_assets(filename, duration_ms, volume=0.4, type="slash"):
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
            raw_noise = (((i * 9301 + 49297) % 233280) / 233280.0) * 2.0 - 1.0
            
            if type == "slash":
                # Clean cinematic swipe / slash
                freq = 220 * math.exp(-progress * 4.0)
                angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(angle)
                filter_damping = math.exp(-progress * 8.0)
                soft_noise = raw_noise * filter_damping * 0.4
                fade_in = min(1.0, t / 0.008)
                decay = math.exp(-t * 14) 
                sample = (fundamental * 0.5 + soft_noise * 0.5) * fade_in
                
            elif type == "scroll":
                # Tactile notch scroll tick
                freq = 140 
                angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(angle)
                snap = raw_noise * 0.15 if i < (sample_rate * 0.003) else 0.0
                fade_in = min(1.0, t / 0.002)
                decay = math.exp(-t * 85) 
                sample = (fundamental * 0.85 + snap) * fade_in

            elif type == "shutdown":
                # --- SERIOUS ELECTROMAGNETIC SYSTEM POWER-DOWN ---
                # Drop from a deep 120Hz fundamental down to an sub-bass 30Hz
                freq = 120 * math.exp(-progress * 3.5)
                angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(angle)
                
                # Add a low, industrial sub-harmonic overtone for heavy physical mass
                sub_angle = 2.0 * math.pi * (freq * 0.5) * t
                sub_bass = math.sin(sub_angle)
                
                # Smoothly fade out the high frequencies immediately, leaving only a deep mechanical vacuum tail
                vacuum_noise = raw_noise * math.exp(-progress * 12.0) * 0