import wave
import math
import struct
import os

def generate_cinematic_ui_sound(filename, duration_ms, volume=0.5, type="slash"):
    sample_rate = 44100
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    
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
            
            # Generate raw pseudo-random white noise (-1.0 to 1.0)
            # This provides the 'air' and 'friction' needed for a slash or texture
            raw_noise = (int(i * 1234567) % 200 - 100) / 100.0
            
            if type == "slash":
                # --- PREMIUM CINEMATIC SLASH / STRONG CLICK ---
                # Combine a heavy low-mid punch tone with a white noise air burst
                freq = 400 * math.exp(-progress * 5.0) # Heavy drop from 400Hz to 80Hz
                tone_angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(tone_angle)
                
                # Dynamic filter: The noise starts sharp/high-passed and closes down
                noise_filter = math.cos(progress * (math.pi / 2))
                textured_noise = raw_noise * noise_filter * 0.6
                
                # Blend: 40% solid physical punch, 60% razor-sharp air slash
                sample = (fundamental * 0.4) + (textured_noise * 0.6)
                
                # Exponential decay that lets the 'tail' of the slash ring out slightly
                decay = math.exp(-t * 35)
                
            else:
                # --- TACTILE COG WHEEL SCROLL ---
                # A distinct, clean 50ms mechanical clunk that you can clearly hear
                # Uses a fixed low-mid frequency tone for a heavy, serious weight
                freq = 220  # A solid, deep G note frequency
                tone_angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(tone_angle)
                
                # Add a sharp crisp snap right at the very beginning of the tick (first 5ms)
                snap = raw_noise * 0.3 if i < (sample_rate * 0.005) else 0.0
                
                sample = (fundamental * 0.8) + snap
                
                # Linear-to-exponential dampening to make it sound like a solid wheel detent
                decay = math.exp(-t * 80)
                
            # Soft-clip limiter to guarantee zero distortion clipping
            final_wave = sample * volume * decay
            final_wave = max(-1.0, min(1.0, final_wave))
            
            # Pack to 16-bit PCM binary
            packed_sample = struct.pack('<h', int(final_wave * 32767))
            wav_file.writeframesraw(packed_sample)

print("Synthesizing cinematic slash and tactile scroll assets...")

# Create click.wav: 120ms total duration for a heavy, stylized mechanical 'slash-click'
generate_cinematic_ui_sound("click.wav", duration_ms=120, volume=0.6, type="slash")

# Create scroll.wav: bumped up to 50ms so it is completely audible and sounds like a serious gear notch
generate_cinematic_ui_sound("scroll.wav", duration_ms=50, volume=0.4, type="scroll")

print("Successfully generated 'click.wav' and 'scroll.wav' inside your project root directory!")