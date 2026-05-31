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
        # Keeps voltage inside steady operational metrics for desktop emulation
        return random.randint(15, 100)

    def _force_immediate_refresh(self):
        """Forces immediate calculations during initialization or layout change steps."""
        self._process_telemetry_cycle()

    def _process_telemetry_cycle(self):
        """Calculates power thresholds and maps text strings across active view states."""
        self.current_battery_pct = self._read_hardware_voltage()

        # Define color profiles based on strict voltage bounds
        if self.current_battery_pct < 20:
            battery_color = "#880000"  # Critical Dark Red
        elif self.current_battery_pct <= 35:
            battery_color = "#FF9900"  # Low Alert Amber
        else:
            battery_color = "#666666"  # Main Menu Gray

        try:
            # 1. Update Battery Status Readout Line
            display_string = f"{self.current_battery_pct}%"
            if self.current_battery_pct < 20:
                display_string += " [!] LOW VOLTAGE"
            
            self.app.update_battery_display(display_string, color=battery_color)
            
            # 2. Update Subscript Song Line (Only if we are sitting inside the Main Menu view frame)
            if self.app.btn_access.winfo_manager() != "":
                if self.current_battery_pct < 20:
                    self.app.update_status_text("▪ VOLTAGE CRITICALY LOW ▪", color="#880000")
                elif self.app.is_playing and self.app.track_list:
                    track_name = self.app.track_list[self.app.current_track_index].replace(".mp3", "")
                    target_text = f"▶ {track_name}"
                    # Guard prevents clearing string offsets on active marquee ticks
                    if self.app.marquee_text != target_text.upper():
                        self.app.update_status_text(target_text, color="#FFB300")
                else:
                    if self.app.marquee_text != "▪ ONLINE ▪":
                        self.app.update_status_text("▪ ONLINE ▪", color="#888888")
        except Exception as e:
            print(f"[Telemetry Exception] Cache bypass: {e}")

    def _execute_ui_pulse_loop(self):
        if not self.is_running:
            return

        self._process_telemetry_cycle()

        # Fire loop every 4 seconds
        if self.is_running:
            self.app.after(4000, self._execute_ui_pulse_loop)