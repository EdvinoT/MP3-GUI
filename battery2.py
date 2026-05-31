import os
import random

class BatteryTelemetry:
    def __init__(self, app_reference):
        self.app = app_reference
        self.is_running = False
        self.current_battery_pct = 100
        self.is_low_battery = False

    def start(self):
        self.is_running = True
        self._execute_ui_pulse_loop()

    def stop(self):
        self.is_running = False

    def get_status_string(self):
        if self.current_battery_pct < 20:
            return "▪ VOLTAGE CRITICALY LOW ▪"
        if hasattr(self.app, 'is_playing') and self.app.is_playing:
            if self.app.track_list:
                track_name = self.app.track_list[self.app.current_track_index].replace(".mp3", "")
                return f"▶ {track_name}"
        return "▪ ONLINE ▪"

    def _read_hardware_voltage(self):
        return random.randint(15, 100)

    def _execute_ui_pulse_loop(self):
        if not self.is_running:
            return

        self.current_battery_pct = self._read_hardware_voltage()

        if self.current_battery_pct < 20:
            self.is_low_battery = True
            battery_color = "#880000"  
        elif self.current_battery_pct <= 35:
            self.is_low_battery = False
            battery_color = "#FF9900"  
        else:
            self.is_low_battery = False
            battery_color = "#666666"  

        try:
            display_string = f"{self.current_battery_pct}%"
            if self.current_battery_pct < 20:
                display_string += " [!] LOW VOLTAGE"
            
            self.app.update_battery_display(display_string, color=battery_color)
            
            # Let the battery pulse cleanly feed metadata to the new marquee engine
            if self.app.btn_access.winfo_manager() != "":
                if self.app.current_battery_pct < 20:
                    self.app.update_status_text("▪ VOLTAGE CRITICALY LOW ▪", color="#880000")
                elif self.app.is_playing and self.app.track_list:
                    track_name = self.app.track_list[self.app.current_track_index].replace(".mp3", "")
                    target_text = f"▶ {track_name}"
                    # Only update if the base text actually changed to protect layout render loops
                    if self.app.raw_status_text != target_text.upper():
                        self.app.update_status_text(target_text, color="#FFB300")
                elif not self.app.is_playing:
                    if self.app.raw_status_text != "▪ ONLINE ▪":
                        self.app.update_status_text("▪ ONLINE ▪", color="#888888")
                
        except Exception as e:
            print(f"[Battery Monitor] Canvas refresh skipped: {e}")

        if self.is_running:
            self.app.after(4000, self._execute_ui_pulse_loop)