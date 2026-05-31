# download_sound_assets.py
import wave
import math
import struct

def generate_smooth_cinematic_assets(filename, duration_ms, volume=0.4, type="slash"):
    sample_rate = 44100
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            progress = i / num_samples
            
            # Create a pseudo-random texture that alternates quickly to reduce piercing hiss
            raw_noise = (((i * 9301 + 49297) % 233280) / 233280.0) * 2.0 - 1.0
            
            if type == "slash":
                # --- SMOOTH CINEMATIC SWIPE / SLASH ---
                # Lower the pitch sweep so it stays in a deep, serious register (220Hz down to 50Hz)
                freq = 220 * math.exp(-progress * 4.0)
                angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(angle)
                
                # Low-pass filter effect: heavily dampens the high-pitched piercing noise as it plays
                filter_damping = math.exp(-progress * 8.0)
                soft_noise = raw_noise * filter_damping * 0.4
                
                # Fade-In (First 8ms): Smooths out the harsh initial pop
                fade_in = min(1.0, t / 0.008)
                
                # Exponential Decay (Slower, natural tail so it NEVER cuts off halfway)
                decay = math.exp(-t * 14) 
                
                sample = (fundamental * 0.5 + soft_noise * 0.5) * fade_in
                
            else:
                # --- TACTILE NOTCH SCROLL TICK ---
                # A very low, round, satisfying wood-block/gear notch mechanical pulse
                freq = 140 
                angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(angle)
                
                # Microscopic soft click at the start
                snap = raw_noise * 0.15 if i < (sample_rate * 0.003) else 0.0
                
                fade_in = min(1.0, t / 0.002)
                decay = math.exp(-t * 85) 
                
                sample = (fundamental * 0.85 + snap) * fade_in
                
            # Bring down master gain and clamp it safely to prevent ear fatigue
            final_wave = sample * volume * decay
            final_wave = max(-0.8, min(0.8, final_wave))
            
            packed_sample = struct.pack('<h', int(final_wave * 32767))
            wav_file.writeframesraw(packed_sample)

print("Compounding smooth, low-fatigue cinematic audio assets...")

# Generate click.wav: Bumps up to 250ms for a long, elegant cinematic air slash swipe
generate_smooth_cinematic_assets("click.wav", duration_ms=250, volume=0.5, type="slash")

# Generate scroll.wav: 40ms deep matte mechanical wheel notch
generate_smooth_cinematic_assets("scroll.wav", duration_ms=40, volume=0.3, type="scroll")

print("Successfully written smoothed 'click.wav' and 'scroll.wav' locally!")