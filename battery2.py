def _execute_ui_pulse_loop(self):
        """Safely updates battery stats without crashing on the new tag architecture."""
        if not self.is_running:
            return

        # 1. Read battery metrics (keep your existing reading logic here)
        self.current_battery_pct = self._read_hardware_voltage() 

        # 2. Determine low battery critical thresholds
        if self.current_battery_pct <= 15:
            self.is_low_battery = True
            battery_color = "#FF3333" # Alert Red
        else:
            self.is_low_battery = False
            battery_color = "#666666" # Stealth Gray

        # 3. SAFE TAG UPDATE: Calls the main app's string-based updater
        try:
            display_string = f"{self.current_battery_pct}%"
            if self.is_low_battery:
                display_string += " ! LOW VOLTAGE"
                
            # This completely bypasses the broken 'sub_text_id' property!
            self.app.update_battery_display(display_string, color=battery_color)
            
        except Exception as e:
            print(f"[Battery Monitor] Canvas refresh skipped: {e}")

        # Loop the thread loop safely
        if self.is_running:
            # Re-run after 5000ms (5 seconds) so it doesn't hog the Pi core
            self.app.after(5000, self._execute_ui_pulse_loop)