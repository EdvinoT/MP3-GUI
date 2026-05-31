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
        
        # Accumulator for tracking phase smoothly over shifting frequencies
        phase = 0.0
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            progress = i / num_samples
            
            raw_noise = (((i * 9301 + 49297) % 233280) / 233280.0) * 2.0 - 1.0
            
            if type == "slash":
                freq = 220 * math.exp(-progress * 4.0)
                angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(angle)
                filter_damping = math.exp(-progress * 8.0)
                soft_noise = raw_noise * filter_damping * 0.4
                fade_in = min(1.0, t / 0.008)
                decay = math.exp(-t * 14) 
                sample = (fundamental * 0.5 + soft_noise * 0.5) * fade_in
                
            elif type == "scroll":
                freq = 140 
                angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(angle)
                snap = raw_noise * 0.15 if i < (sample_rate * 0.003) else 0.0
                fade_in = min(1.0, t / 0.002)
                decay = math.exp(-t * 85) 
                sample = (fundamental * 0.85 + snap) * fade_in
                
            elif type == "shutdown":
                # --- TACTILE INDUSTRIAL POWER DOWN ---
                # Linearly drop frequency from a solid 140Hz down to a heavy 30Hz bass floor
                current_freq = 140.0 - (110.0 * progress)
                
                # Keep phase aligned smoothly across changing pitch to prevent internal pops
                phase += (2.0 * math.pi * current_freq) / sample_rate
                fundamental = math.sin(phase)
                
                # Add a low mechanical hum texture
                hum = math.sin(phase * 0.5) * 0.25
                
                # Slower fade out to mimic core generators winding down
                decay = 1.0 - progress 
                fade_in = min(1.0, t / 0.015) # Soft edge
                
                sample = (fundamental * 0.75 + hum) * fade_in
                
            final_wave = sample * volume * decay
            final_wave = max(-0.8, min(0.8, final_wave))
            
            packed_sample = struct.pack('<h', int(final_wave * 32767))
            wav_file.writeframesraw(packed_sample)

print("Compounding smooth, low-fatigue cinematic audio assets...")

generate_smooth_cinematic_assets("click.wav", duration_ms=250, volume=0.5, type="slash")
generate_smooth_cinematic_assets("scroll.wav", duration_ms=40, volume=0.3, type="scroll")

# Generate shutdown.wav (650ms long industrial engine power drain)
generate_smooth_cinematic_assets("shutdown.wav", duration_ms=650, volume=0.6, type="shutdown")

print("Successfully written local asset files!")