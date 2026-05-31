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
        return random.randint(15, 100)

    def _process_telemetry_cycle(self):
        self.current_battery_pct = self._read_hardware_voltage()

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
            
            # Double-check that menu buttons are still packed before pushing text
            if self.app.btn_access.winfo_manager() != "":
                self.app.update_battery_display(display_string, color=battery_color)
                
                if self.current_battery_pct < 20:
                    self.app.update_status_text("▪ VOLTAGE CRITICALY LOW ▪", color="#880000")
                elif self.app.is_playing and self.app.track_list:
                    track_name = self.app.track_list[self.app.current_track_index].replace(".mp3", "")
                    target_text = f"▶ {track_name}"
                    if self.app.marquee_text != target_text.upper():
                        self.app.update_status_text(target_text, color="#FFB300")
                else:
                    if self.app.marquee_text != "▪ ONLINE ▪":
                        self.app.update_status_text("▪ ONLINE ▪", color="#888888")
            else:
                # Force visibility clear down if we are inside a sub-menu
                self.app.update_battery_display("", color=battery_color)
                
        except Exception as e:
            print(f"[Telemetry Sync Warning] Base reference drop: {e}")

    def _execute_ui_pulse_loop(self):
        if not self.is_running:
            return

        self._process_telemetry_cycle()

        if self.is_running:
            self.app.after(4000, self._execute_ui_pulse_loop)