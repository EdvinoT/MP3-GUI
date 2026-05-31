#!/usr/bin/env python3
"""
Pocket-sized MP3 Player for Raspberry Pi Zero W 2
Optimized for 2.42" OLED display + GPIO physical buttons

Can run on Mac for testing (OLED/GPIO won't work)
Fully functional on Raspberry Pi
"""

import pygame
import os
import time
from threading import Thread
import sys

# Display
try:
    from PIL import Image, ImageDraw, ImageFont
    DISPLAY_AVAILABLE = True
except ImportError:
    DISPLAY_AVAILABLE = False
    print("Warning: PIL library not available")

# GPIO (only on Raspberry Pi)
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    GPIO = None
    if sys.platform.startswith('linux'):
        print("Warning: Running on Linux but GPIO not available (not on Pi?)")
    else:
        print("Note: GPIO not available on this platform (testing mode)")

# OLED (only on Raspberry Pi)
try:
    import Adafruit_SSD1306
    OLED_AVAILABLE = True
except ImportError:
    OLED_AVAILABLE = False
    if GPIO_AVAILABLE:
        print("Warning: OLED library not available")


class CompactMP3Player:
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Paths
        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        self.tracks_dir = os.path.join(self.dir_path, "tracks")
        if not os.path.exists(self.tracks_dir):
            os.makedirs(self.tracks_dir)
        
        # Player state
        self.track_list = []
        self.current_index = 0
        self.is_playing = False
        self.volume = 100
        self.current_time = 0
        self.total_time = 0
        
        # Load tracks
        self.load_tracks()
        
        # Initialize OLED display
        self.init_display()
        
        # Initialize GPIO buttons
        self.init_gpio()
        
        # Display update thread
        self.display_thread = Thread(target=self.display_loop, daemon=True)
        self.display_thread.start()
        
        print("\n=== MP3 Player Initialized ===", flush=True)
        print(f"Platform: {sys.platform}", flush=True)
        print(f"GPIO available: {GPIO_AVAILABLE}", flush=True)
        print(f"Display available: {self.display is not None}", flush=True)
        print(f"Tracks loaded: {len(self.track_list)}", flush=True)
        print("================================\n", flush=True)
    
    def init_display(self):
        """Initialize 2.42" OLED I2C display"""
        if not DISPLAY_AVAILABLE:
            self.display = None
            print("Display: Not available (testing mode)", flush=True)
            return
        
        if not OLED_AVAILABLE:
            self.display = None
            print("Display: PIL available but OLED driver not installed", flush=True)
            return
        
        try:
            # I2C address 0x3C for 2.42" OLED
            self.display = Adafruit_SSD1306.SSD1306_128_64(i2c_bus=1, addr=0x3C)
            self.display.begin()
            self.display.display()
            print("Display: OLED initialized successfully", flush=True)
        except Exception as e:
            print(f"Display: OLED initialization failed: {e}", flush=True)
            self.display = None
    
    def init_gpio(self):
        """Setup GPIO buttons"""
        if not GPIO_AVAILABLE:
            print("GPIO: Not available (testing mode - buttons won't work)", flush=True)
            return
        
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Button pins
            self.buttons = {
                17: ('PLAY', self.toggle_play),
                27: ('NEXT', self.next_track),
                22: ('PREV', self.prev_track),
                23: ('VOL_UP', self.volume_up),
                24: ('VOL_DOWN', self.volume_down),
            }
            
            # Setup each button
            for pin, (name, callback) in self.buttons.items():
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(
                    pin, GPIO.FALLING,
                    callback=lambda x, cb=callback: cb(),
                    bouncetime=300
                )
            
            print(f"GPIO: Buttons initialized on pins: {list(self.buttons.keys())}", flush=True)
        except Exception as e:
            print(f"GPIO: Button setup failed: {e}", flush=True)
    
    def load_tracks(self):
        """Load MP3 files from tracks directory"""
        self.track_list = [
            f for f in os.listdir(self.tracks_dir)
            if f.lower().endswith('.mp3')
        ]
        self.track_list.sort()
        print(f"Loaded {len(self.track_list)} tracks", flush=True)
    
    def toggle_play(self):
        """Play/Pause toggle"""
        if not self.track_list:
            return
        
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
        else:
            if pygame.mixer.music.get_pos() > 0:
                pygame.mixer.music.unpause()
            else:
                self.play_track(self.current_index)
            self.is_playing = True
    
    def next_track(self):
        """Skip to next track"""
        if not self.track_list:
            return
        self.current_index = (self.current_index + 1) % len(self.track_list)
        self.play_track(self.current_index)
    
    def prev_track(self):
        """Go to previous track"""
        if not self.track_list:
            return
        self.current_index = (self.current_index - 1) % len(self.track_list)
        self.play_track(self.current_index)
    
    def volume_up(self):
        """Increase volume"""
        self.volume = min(100, self.volume + 10)
        pygame.mixer.music.set_volume(self.volume / 100)
    
    def volume_down(self):
        """Decrease volume"""
        self.volume = max(0, self.volume - 10)
        pygame.mixer.music.set_volume(self.volume / 100)
    
    def play_track(self, index):
        """Load and play track"""
        if not self.track_list or index < 0 or index >= len(self.track_list):
            return
        
        track_path = os.path.join(self.tracks_dir, self.track_list[index])
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.current_time = 0
            print(f"Playing: {self.track_list[index]}", flush=True)
        except Exception as e:
            print(f"Error playing track: {e}", flush=True)
            self.is_playing = False
    
    def display_loop(self):
        """Continuously update OLED display"""
        if not self.display:
            print("Display loop: Skipped (no display available)", flush=True)
            return
        
        while True:
            try:
                self.update_display()
                time.sleep(0.5)  # Update every 500ms
            except Exception as e:
                print(f"Display update error: {e}", flush=True)
    
    def update_display(self):
        """Update OLED content"""
        if not self.display:
            return
        
        # Create blank image
        image = Image.new('1', (128, 64))
        draw = ImageDraw.Draw(image)
        
        # Try to use nice font, fallback to default
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
            status_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        except:
            title_font = ImageFont.load_default()
            status_font = ImageFont.load_default()
        
        # Current track
        if self.track_list:
            track_name = self.track_list[self.current_index].replace('.mp3', '')
            # Truncate if too long
            if len(track_name) > 20:
                track_name = track_name[:17] + "..."
            draw.text((0, 0), track_name, font=title_font, fill=1)
        else:
            draw.text((0, 0), "No tracks", font=title_font, fill=1)
        
        # Status line
        status = "●" if self.is_playing else "○"
        status_line = f"{status} {self.current_index + 1}/{len(self.track_list)} VOL:{self.volume}%"
        draw.text((0, 16), status_line, font=status_font, fill=1)
        
        # Progress bar (simple)
        draw.rectangle((0, 28, 128, 30), outline=1)
        if self.total_time > 0:
            progress_width = int((self.current_time / self.total_time) * 128)
            draw.rectangle((0, 28, progress_width, 30), fill=1)
        
        # Time display
        current_str = self.format_time(self.current_time)
        total_str = self.format_time(self.total_time)
        draw.text((0, 35), f"{current_str} / {total_str}", font=status_font, fill=1)
        
        # Battery level (if available)
        try:
            import subprocess
            result = subprocess.run(['vcgencmd', 'measure_volts'], capture_output=True, text=True)
            battery_info = result.stdout.strip()
        except:
            battery_info = "PWR"
        
        draw.text((0, 50), battery_info, font=status_font, fill=1)
        
        # Display on OLED
        self.display.image(image)
        self.display.display()
    
    def format_time(self, ms):
        """Format milliseconds to MM:SS"""
        seconds = int(ms / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def update_track_time(self):
        """Update current playback time"""
        if self.is_playing:
            self.current_time = pygame.mixer.music.get_pos()
    
    def cleanup(self):
        """Clean shutdown"""
        print("Shutting down...", flush=True)
        pygame.mixer.quit()
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
            except:
                pass


def main():
    player = CompactMP3Player()
    
    try:
        # Keep running
        while True:
            player.update_track_time()
            time.sleep(0.1)
    except KeyboardInterrupt:
        player.cleanup()
        print("Shutdown complete", flush=True)


if __name__ == "__main__":
    main()
