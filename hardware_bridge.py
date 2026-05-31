import os
import sys
import threading

# 1. Handle optional ALSA Audio for Hardware Volume Control
try:
    import alsaaudio
    # 'Headphone' or 'Master' are standard audio channels on Raspberry Pi audio hats
    try:
        SYSTEM_MIXER = alsaaudio.Mixer('Headphone')
    except Exception:
        try:
            SYSTEM_MIXER = alsaaudio.Mixer('Master')
        except Exception:
            SYSTEM_MIXER = None
except ImportError:
    SYSTEM_MIXER = None

# 2. Handle optional Mutagen for clean ID3 track data mapping
try:
    from mutagen.mp3 import MP3
    from mutagen.easyid3 import EasyID3
except ImportError:
    MP3 = None
    EasyID3 = None

# 3. Handle optional GPIO framework for physical tactical button hooks
try:
    from gpiozero import Button
except ImportError:
    Button = None


class HardwareBridge:
    def __init__(self, main_app_instance):
        """
        Injects advanced Quality of Life hardware layers into the player engine
        without cluttering the main script execution file blocks.
        """
        self.app = main_app_instance
        self.hardware_volume_pct = 80  # Default startup safety fallback volume
        
        print("\n=== COUPLING HARDWARE EXTENSION BRIDGE ===")
        self._initialize_volume_subsystem()
        self._patch_metadata_engine()
        self._bind_gpio_pins()
        print("==========================================\n")

    def _initialize_volume_subsystem(self):
        """Registers system volume telemetry fields onto the interface canvas."""
        if SYSTEM_MIXER:
            try:
                self.hardware_volume_pct = SYSTEM_MIXER.getvolume()[0]
                print(f"[ALSA] Coupled hardware mixer card channel. Native Vol: {self.hardware_volume_pct}%")
            except Exception as e:
                print(f"[ALSA] Control link failed: {e}")
        else:
            print("[ALSA] Subsystem offline. Defaulting to software emulation presets.")

        # Append visual Volume metadata coordinates directly to the canvas layers
        self.vol_text_id = self.app.bg_canvas.create_text(
            420, 25, text=f"VOL {self.hardware_volume_pct}%",
            font=("Arial", 9, "bold"), fill="#666666", anchor="e"
        )
        
        # Bind keyboard shortcuts (+/- keys) so you can test volume on your PC right now!
        self.app.bind("<plus>", lambda e: self.adjust_volume(5))
        self.app.bind("<equal>", lambda e: self.adjust_volume(5)) # Standard shared key mapping
        self.app.bind("<minus>", lambda e: self.adjust_volume(-5))

    def adjust_volume(self, delta):
        """Changes system master volume up or down and prints to screen."""
        self.hardware_volume_pct = max(0, min(100, self.hardware_volume_pct + delta))
        
        if SYSTEM_MIXER:
            try:
                SYSTEM_MIXER.setvolume(self.hardware_volume_pct)
            except Exception as e:
                print(f"[ALSA] Write failure: {e}")
        
        # Update the text on your layout instantly
        self.app.bg_canvas.itemconfig(self.vol_text_id, text=f"VOL {self.hardware_volume_pct}%")

    def _patch_metadata_engine(self):
        """Intercepts track loading requests to pull clean title tag data fields."""
        if MP3 and EasyID3:
            print("[MUTAGEN] Deep indexing functional. Parsing structural ID3 tag assets.")
            
            # Wrap the original play method cleanly
            original_play_method = self.app.play_current_track
            
            def custom_metadata_play_wrapper():
                # Fire standard core stream loader
                original_play_method()
                
                # Instantly extract true track tags safely in the background
                if self.app.track_list:
                    track_file = self.app.track_list[self.app.current_track_index]
                    track_path = os.path.join(self.app.tracks_dir, track_file)
                    
                    try:
                        audio = MP3(track_path, ID3=EasyID3)
                        title = audio.get('title', [None])[0]
                        artist = audio.get('artist', [None])[0]
                        
                        if title and artist:
                            display_tag = f"▶ {title} - {artist}"
                        elif title:
                            display_tag = f"▶ {title}"
                        else:
                            display_tag = f"▶ {track_file.replace('.mp3', '')}"
                            
                        self.app.update_status_text(display_tag, color="#FFB300")
                    except Exception:
                        pass # Rollback fallback string handled gracefully by core
                        
            # Replace the runtime link
            self.app.play_current_track = custom_metadata_play_wrapper
        else:
            print("[MUTAGEN] Libraries unindexed. Defaulting display profile to raw filenames.")

    def _bind_gpio_pins(self):
        """Asynchronously maps physical button presses straight to the UI functions."""
        if Button:
            print("[GPIO] Board detected. Initializing asynchronous tactile wire pathways.")
            try:
                # Pinout allocation matches typical handheld chassis mapping guidelines
                self.hw_btn_next = Button(17, bounce_time=0.05) # Pin 17 maps to physical track jump
                self.hw_btn_prev = Button(27, bounce_time=0.05) # Pin 27 maps to back tracking
                self.hw_btn_play = Button(22, bounce_time=0.05) # Pin 22 handles physical pause/unpause
                
                # Point the physical wiring logic straight to your main app actions
                self.hw_btn_next.when_pressed = self.app.next_track
                self.hw_btn_prev.when_pressed = self.app.prev_track
                self.hw_btn_play.when_pressed = self.app.toggle_play
                
            except Exception as gpio_err:
                print(f"[GPIO] Setup blocked by board configuration limits: {gpio_err}")
        else:
            print("[GPIO] Subsystem bypassed. Listening exclusively to interface canvas bindings.")