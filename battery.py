# battery.py
import threading
import time
import math

try:
    import psutil
    HAS_BATTERY_DRIVERS = True
except ImportError:
    HAS_BATTERY_DRIVERS = False

class BatteryTelemetry:
    def __init__(self, app_instance):
        self.app = app_instance
        self.current_battery_pct = 100
        self.is_low_battery = False
        self.telemetry_alive = True
        self.debug_force_low = False  # Set to True to test low battery instantly!

    def start(self):
        t = threading.Thread(target=self._telemetry_worker, daemon=True)
        t.start()
        self._execute_ui_pulse_loop()

    def stop(self):
        self.telemetry_alive = False

    def get_status_string(self):
        if not self.app.track_list:
            return "▪ NO SONGS LOADED ▪"
        elif self.app.is_playing:
            clean_name = self.app.track_list[self.app.current_track_index].replace(".mp3", "")
            return f"▪ PLAYING: {clean_name} ▪"
        else:
            return "▪ ONLINE ▪"

    def _telemetry_worker(self):
        while self.telemetry_alive:
            if self.debug_force_low:
                self.current_battery_pct = 14
                self.is_low_battery = True
            elif HAS_BATTERY_DRIVERS:
                try:
                    battery = psutil.sensors_battery()
                    if battery is not None:
                        self.current_battery_pct = int(battery.percent)
                        self.is_low_battery = (self.current_battery_pct <= 20 and not battery.power_plugged)
                    else:
                        self.is_low_battery = False
                except:
                    self.is_low_battery = False
            else:
                self.is_low_battery = False

            # If battery is healthy, keep everything light gray
            if not self.is_low_battery and self.telemetry_alive:
                self.app.update_status_text(self.get_status_string(), color="#BBBBBB")
                self.app.update_battery_display(f"{self.current_battery_pct}%", color="#BBBBBB")
            
            time.sleep(2.0)

    def _execute_ui_pulse_loop(self):
        if not self.telemetry_alive:
            return

        if self.is_low_battery:
            current_ms = time.time() * 3.5
            alpha_factor = (math.cos(current_ms) + 1.0) / 2.0
            
            # Pure dark red (#880000) pulsing up to a warning red (#FF3333)
            r = int(0x88 + (0x77 * alpha_factor))
            g = int(0x00 + (0x33 * alpha_factor))
            b = int(0x00 + (0x33 * alpha_factor))
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            self.app.update_status_text("▪ VOLTAGE DROP CRITICAL ▪", color=hex_color)
            self.app.update_battery_display(f"{self.current_battery_pct}%", color=hex_color)
        else:
            # Revert back to light gray when safe
            if self.app.sub_text_id is not None:
                current_color = self.app.bg_canvas.itemcget(self.app.sub_text_id, "fill")
                if current_color.startswith("#") and current_color != "#BBBBBB":
                    self.app.update_status_text(self.get_status_string(), color="#BBBBBB")
                    self.app.update_battery_display(f"{self.current_battery_pct}%", color="#BBBBBB")

        self.app.after(33, self._execute_ui_pulse_loop)