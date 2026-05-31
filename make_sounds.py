import wave
import math
import struct
import os
import time

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
            
            # Raw white noise component
            raw_noise = (int(i * 1234567) % 200 - 100) / 100.0
            
            if type == "slash":
                # Heavy drop from 400Hz to 80Hz + noise overlay
                freq = 400 * math.exp(-progress * 5.0)
                tone_angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(tone_angle)
                
                noise_filter = math.cos(progress * (math.pi / 2))
                textured_noise = raw_noise * noise_filter * 0.7
                
                sample = (fundamental * 0.3) + (textured_noise * 0.7)
                decay = math.exp(-t * 30)
                
            else:
                # TACTILE COG WHEEL SCROLL (Deep, physical clunk)
                freq = 200 
                tone_angle = 2.0 * math.pi * freq * t
                fundamental = math.sin(tone_angle)
                
                # Snappy transient click at the start
                snap = raw_noise * 0.4 if i < (sample_rate * 0.008) else 0.0
                
                sample = (fundamental * 0.7) + snap
                decay = math.exp(-t * 60)
                
            final_wave = sample * volume * decay
            final_wave = max(-1.0, min(1.0, final_wave))
            
            packed_sample = struct.pack('<h', int(final_wave * 32767))
            wav_file.writeframesraw(packed_sample)

print("Synthesizing cinematic assets...")
generate_cinematic_ui_sound("click.wav", duration_ms=140, volume=0.7, type="slash")
generate_cinematic_ui_sound("scroll.wav", duration_ms=60, volume=0.5, type="scroll")
print("Generated new audio assets.")

# --- AUTOMATIC PLAYBACK TESTER ---
print("\n--- STARTING LIVE AUDIO TEST ---")
try:
    import pygame
    pygame.mixer.init()
    
    click_sound = pygame.mixer.Sound("click.wav")
    scroll_sound = pygame.mixer.Sound("scroll.wav")
    
    print("Playing 'click.wav' (Slash Click)...")
    click_sound.play()
    time.sleep(0.5) # Wait half a second
    
    print("Simulating a fast mouse scroll (3 ticks)...")
    for _ in range(3):
        scroll_sound.play()
        time.sleep(0.12) # Gap between scroll notches
        
    print("--- TEST COMPLETE ---")
except ImportError:
    print("Could not run automated test because 'pygame' is not installed.")