import os
import sys
import threading
import time

# Optional ALSA Audio integration
try:
    import alsaaudio
    try:
        SYSTEM_MIXER = alsaaudio.Mixer('Headphone')
    except Exception:
        try:
            SYSTEM_MIXER = alsaaudio.Mixer('Master')
        except Exception:
            SYSTEM_MIXER = None
except ImportError:
    SYSTEM_MIXER = None

# Optional Mutagen integration
try:
    from mutagen.mp3 import MP3
    from mutagen.easyid3 import EasyID3
except ImportError:
    MP3 = None
    EasyID3 = None

# Optional GPIO integration for buttons and the EC11 Rotary Encoder
try:
    from gpiozero import Button, RotaryEncoder
except ImportError:
    Button = None
    RotaryEncoder = None


class HardwareBridge:
    def __init__(self, main_app_instance):
        """
        Comprehensive hardware abstraction layer managing visual telemetry,
        iPod-style rotary navigation, and resource-saving background monitors.
        """
        self.app = main_app_instance
        self.hardware_volume_pct = 80  # Default startup volume safety fallback
        self.last_interaction_time = time.time()
        self.screen_is_awake = True
        
        print("\n=== INITIALIZING FINAL HARDWARE DEPLOYMENT BRIDGE ===")
        self._initialize_volume_subsystem()
        self._patch_metadata_engine()
        self._bind_hardware_controls()
        self._start_power_management_loops()
        print("====================================================\n")

    def _initialize_volume_subsystem(self):
        """Registers system volume display layers onto the main canvas."""
        if SYSTEM_MIXER:
            try:
                self.hardware_volume_pct = SYSTEM_MIXER.getvolume()[0]
                print(f"[ALSA] Master channel engaged. Volume: {self.hardware_volume_pct}%")
            except Exception as e:
                print(f"[ALSA] Mixer hook dropped: {e}")
        else:
            print("[ALSA] Subsystem offline. Emulating virtual audio controls.")

        self.vol_text_id = self.app.bg_canvas.create_text(
            420, 25, text=f"VOL {self.hardware_volume_pct}%",
            font=("Arial", 9, "bold"), fill="#666666", anchor="e"
        )
        
        # Test keys for computer-based testing (+ / - keys)
        self.app.bind("<plus>", lambda e: self.adjust_volume(5))
        self.app.bind("<equal>", lambda e: self.adjust_volume(5))
        self.app.bind("<minus>", lambda e: self.adjust_volume(-5))

    def adjust_volume(self, delta):
        """Alters volume levels and updates screen tracking layers."""
        self.poke_activity_timer()
        self.hardware_volume_pct = max(0, min(100, self.hardware_volume_pct + delta))
        
        if SYSTEM_MIXER:
            try:
                SYSTEM_MIXER.setvolume(self.hardware_volume_pct)
            except Exception as e:
                print(f"[ALSA] Write failure: {e}")
        
        self.app.bg_canvas.itemconfig(self.vol_text_id, text=f"VOL {self.hardware_volume_pct}%")

    def _patch_metadata_engine(self):
        """Wraps track playing routines to fetch clean ID3 metadata tags."""
        if MP3 and EasyID3:
            print("[MUTAGEN] Metadata engine hooked. Active parsing enabled.")
            original_play_method = self.app.play_current_track
            
            def custom_metadata_play_wrapper():
                original_play_method()
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
                        pass
            self.app.play_current_track = custom_metadata_play_wrapper
        else:
            print("[MUTAGEN] Fallback active. Displaying raw file configurations.")

    def _bind_hardware_controls(self):
        """Wires the physical iPod-style EC11 click-wheel encoder to internal functions."""
        if RotaryEncoder and Button:
            print("[HARDWARE] Activating iPod-style EC11 click-wheel encoder architecture...")
            try:
                # 1. Map the dial spinning mechanics (Data Pins 23 and 24)
                self.dial = RotaryEncoder(23, 24, bounce_time=0.01)
                self.dial.when_rotated_clockwise = lambda: [self.poke_activity_timer(), self.app.next_track()]
                self.dial.when_rotated_counter_clockwise = lambda: [self.poke_activity_timer(), self.app.prev_track()]
                
                # 2. Map the physical shaft click action (Pin 22)
                self.dial_button = Button(22, bounce_time=0.05)
                self.dial_button.when_pressed = lambda: [self.poke_activity_timer(), self.app.toggle_play()]
                
                print("[GPIO] EC11 Pins registered (Dial: 23/24, Button: 22). Listening for input.")
            except Exception as e:
                print(f"[GPIO] Wiring register bypassed: {e}")
        else:
            print("[GPIO] Standalone test setup. Control loops listening exclusively to simulation assets.")

    def poke_activity_timer(self):
        """Resets the sleep countdown whenever the user interacts with the machine."""
        self.last_interaction_time = time.time()
        if not self.screen_is_awake:
            self.set_backlight_state(awake=True)

    def set_backlight_state(self, awake):
        """Controls system backlighting to prevent burn-in or battery drainage."""
        self.screen_is_awake = awake
        
        # Check if the Raspberry Pi backlight directory actually exists before running sudo
        rpi_backlight_path = "/sys/class/backlight/rpi_backlight/bl_power"
        has_rpi_backlight = os.path.exists(rpi_backlight_path)

        if awake:
            print("[POWER] System wake command processed. Screen backlight ON.")
            if has_rpi_backlight:
                os.system(f"echo 0 | sudo tee {rpi_backlight_path} > /dev/null 2>&1")
            else:
                print("[SIMULATION] Mac/PC detected: Skipping physical backlight ON command.")
        else:
            print("[POWER] Display timeout reached. Screen backlight OFF to preserve juice.")
            if has_rpi_backlight:
                os.system(f"echo 1 | sudo tee {rpi_backlight_path} > /dev/null 2>&1")
            else:
                print("[SIMULATION] Mac/PC detected: Skipping physical backlight OFF command.")

    def _start_power_management_loops(self):
        """Spawns separate daemon threads to safeguard hardware health parameters."""
        # Bind screen clicks to reset the sleep timer
        self.app.bind("<Button-1>", lambda e: self.poke_activity_timer())
        
        # Power management execution loop thread
        def power_loop():
            while self.app.running:
                time.sleep(2)
                
                # A. Handle Auto-Sleep backlighting (60 second threshold limit)
                if self.screen_is_awake and (time.time() - self.last_interaction_time > 60):
                    # Only dim the panel if music is currently streaming out
                    if self.app.is_playing:
                        self.app.after(0, lambda: self.set_backlight_state(awake=False))
                
                # B. Handle Crucial Low-Voltage Protection Safeguards
                if hasattr(self.app, 'battery_monitor'):
                    pct = self.app.battery_monitor.current_battery_pct
                    if pct <= 5 and pct > 0:
                        print("[CRITICAL] Power cell depleted below safety levels! Running forced emergency safety park.")
                        self.app.after(0, self._trigger_emergency_shutdown)
                        break

        p_thread = threading.Thread(target=power_loop)
        p_thread.daemon = True
        p_thread.start()

    def _trigger_emergency_shutdown(self):
        """Safely stops threads, flushes caches, and powers down the computer board."""
        self.app.update_status_text("▪ VOLTAGE CRITICAL - SHUTTING DOWN ▪", color="#FF0000")
        self.app.update()
        time.sleep(2)
        
        # Shut down python app loops cleanly
        self.app.running = False
        try:
            import pygame
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception:
            pass
            
        # Only issue full hardware shutdown command if running on a real Pi environment
        if os.path.exists("/sys/class/backlight/rpi_backlight/bl_power"):
            os.system("sudo shutdown -h now")
        else:
            print("[SIMULATION] Emergency exit finished. Skipping OS-level hardware shutdown.")
            
        sys.exit()