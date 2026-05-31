# battery_telemetry.py
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
        """
        Handles independent hardware battery scanning and warning pulses.
        :param app_instance: The main SurrealPlayerApp instance so we can modify its UI.
        """
        self.app = app_instance
        self.current_battery_pct = 100
        self.is_low_battery = False
        self.telemetry_alive = True

        # Change this to True to test the pulsing critical warning right away!
        self.debug_force_low = False 

    def start(self):
        """Spawns the hardware monitoring thread and kicks off the Tkinter pulse animation."""
        t = threading.Thread(target=self._telemetry_worker, daemon=True)
        t.start()
        self._execute_ui_pulse_loop()

    def stop(self):
        """Safely stops the telemetry loop loops during application destruction."""
        self.telemetry_alive = False

    def get_status_string(self):
        """Calculates standard status text strings based on application music states."""
        if not self.app.track_list:
            return "▪ NO SONGS LOADED ▪"
        elif self.app.is_playing:
            clean_name = self.app.track_list[self.app.current_track_index].replace(".mp3", "")
            return f"▪ PLAYING: {clean_name} [{self.current_battery_pct}%] ▪"
        else:
            return f"▪ ONLINE [{self.current_battery_pct}%] ▪"

    def _telemetry_worker(self):
        """Background thread worker pulling data from OS battery sensors."""
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

            # If things are healthy, make sure the regular status text displays safely
            if not self.is_low_battery and self.telemetry_alive:
                self.app.update_status_text(self.get_status_string(), color="#666666")
            
            time.sleep(4.0)

    def _execute_ui_pulse_loop(self):
        """Renders the smooth red warning pulse on the main loop thread at 30 FPS."""
        if not self.telemetry_alive:
            return

        if self.is_low_battery:
            current_ms = time.time() * 3.5
            alpha_factor = (math.cos(current_ms) + 1.0) / 2.0
            
            r = int(0x1A + (0xE5 * alpha_factor))
            g = int(0x05 + (0x2E * alpha_factor))
            b = int(0x05 + (0x2E * alpha_factor))
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            warning_text = f"▪ VOLTAGE DROP CRITICAL [{self.current_battery_pct}%] ▪"
            self.app.update_status_text(warning_text, color=hex_color)
        else:
            # Cleanly recover back to default gray if plug is re-introduced
            if self.app.sub_text_id is not None:
                current_color = self.app.bg_canvas.itemcget(self.app.sub_text_id, "fill")
                if current_color.startswith("#") and current_color != "#666666":
                    self.app.update_status_text(self.get_status_string(), color="#666666")

        # Keep loop cycling every ~33ms
        self.app.after(33, self._execute_ui_pulse_loop)