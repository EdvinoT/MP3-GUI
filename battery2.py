import random

class BatteryTelemetry:
    def __init__(self, app_reference):
        self.app = app_reference
        self.is_running = False
        self.current_battery_pct = 100

    def start(self):
        self.is_running = True
        self._execute_ui_pulse_loop()

    def stop(self):
        self.is_running = False

    def _read_hardware_voltage(self):
        if self.current_battery_pct > 5:
            return self.current_battery_pct - 1
        else:
            return 100 

    def _process_telemetry_cycle(self):
        # Only decrease battery percentage if this function is triggered by the automatic 4-second loop
        # (This prevents rapid battery draining when clicking back and forth through menus)
        # We handle that check inside the loop calling block directly.
        pass

    def _execute_telemetry_render(self):
        if self.current_battery_pct < 20:
            battery_color = "#880000"  
        elif self.current_battery_pct <= 35:
            battery_color = "#FF9900"  
        else:
            battery_color = "#666666"  

        try:
            display_string = f"{self.current_battery_pct}%"
            if self.current_battery_pct < 20:
                display_string += " [!] LOW VOLTAGE"
            
            if self.app.btn_access.winfo_manager() != "":
                self.app.update_battery_display(display_string, color=battery_color)
                
                if self.current_battery_pct < 20:
                    self.app.update_status_text("▪ VOLTAGE CRITICALY LOW ▪", color="#880000")
                elif self.app.is_playing and self.app.track_list:
                    track_name = self.app.track_list[self.app.current_track_index].replace(".mp3", "")
                    target_text = f"▶ {track_name}"
                    # Guard prevents restarting the marquee loop if the song name is identical
                    if self.app.marquee_text != target_text.upper():
                        self.app.update_status_text(target_text, color="#FFB300")
                else:
                    if self.app.marquee_text != "▪ ONLINE ▪":
                        self.app.update_status_text("▪ ONLINE ▪", color="#888888")
            else:
                self.app.update_battery_display("", color=battery_color)
                
        except Exception as e:
            print(f"[Telemetry Render Warning] skipped: {e}")

    def _process_telemetry_cycle(self):
        """Forced instant manual execution layer."""
        self._execute_telemetry_render()

    def _execute_ui_pulse_loop(self):
        if not self.is_running:
            return

        # Advance battery drain sequence
        self.current_battery_pct = self._read_hardware_voltage()
        self._execute_telemetry_render()

        if self.is_running:
            self.app.after(4000, self._execute_ui_pulse_loop)