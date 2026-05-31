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
                display_name = track_name if len(track_name) < 24 else track_name[:21] + "..."
                return f"▶ {display_name}"
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
            
            # FIXED MONITOR LOGIC: Updates main menu screen with song name dynamically as background cycles
            if self.app.btn_access.winfo_manager() != "":
                if self.current_battery_pct < 20:
                    self.app.update_status_text("▪ VOLTAGE CRITICALY LOW ▪", color="#880000")
                elif self.app.is_playing and self.app.track_list:
                    track_name = self.app.track_list[self.app.current_track_index].replace(".mp3", "")
                    display_name = track_name if len(track_name) < 24 else track_name[:21] + "..."
                    self.app.update_status_text(f"▶ {display_name}", color="#FFB300") # Muted Amber Text Update
                elif not self.app.is_playing:
                    self.app.update_status_text("▪ ONLINE ▪", color="#888888")
                
        except Exception as e:
            print(f"[Battery Monitor] Canvas refresh skipped: {e}")

        if self.is_running:
            self.app.after(4000, self._execute_ui_pulse_loop)