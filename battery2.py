import os
import random

class BatteryTelemetry:
    def __init__(self, app_reference):
        """Initializes the background power monitor thread framework."""
        self.app = app_reference
        self.is_running = False
        self.current_battery_pct = 100
        self.is_low_battery = False

    def start(self):
        """Starts the looping daemon updater engine."""
        self.is_running = True
        self._execute_ui_pulse_loop()

    def stop(self):
        """Safely stops the loop before application destruction."""
        self.is_running = False

    def get_status_string(self):
        """Returns the localized system telemetry notification payload."""
        if self.is_low_battery:
            return "▪ VOLTAGE DROP CRITICAL ▪"
        
        # If music is playing, let main2.py handle showing the song name.
        # This acts as the safe system fallback message.
        if hasattr(self.app, 'is_playing') and self.app.is_playing:
            return "▪ STREAMING AUDIO ▪"
        
        return "▪ ONLINE ▪"

    def _read_hardware_voltage(self):
        """Reads mock battery percentage. Simulates power drain over time."""
        # For desktop testing/fallback, we dynamically pick a healthy percentage.
        # Replace this logic if you are mapping to actual Raspberry Pi GPIO/I2C power pins.
        return random.randint(85, 100)

    def _execute_ui_pulse_loop(self):
        """Safely updates battery stats without crashing on the new tag architecture."""
        if not self.is_running:
            return

        # 1. Update internal state metrics
        self.current_battery_pct = self._read_hardware_voltage()

        # 2. Set structural safety flags
        if self.current_battery_pct <= 15:
            self.is_low_battery = True
            battery_color = "#FF3333"  # Warning Red
        else:
            self.is_low_battery = False
            battery_color = "#666666"  # Subtle Menu Gray

        # 3. Fire thread-safe canvas tag updates
        try:
            display_string = f"{self.current_battery_pct}%"
            if self.is_low_battery:
                display_string += " ! LOW VOLTAGE"
            
            # Cleanly commands main2.py to update the battery_sub tag row
            self.app.update_battery_display(display_string, color=battery_color)
            
        except Exception as e:
            print(f"[Battery Monitor] Canvas refresh skipped: {e}")

        # 4. Schedule the next loop pulse (Runs every 5 seconds to protect Pi CPU)
        if self.is_running:
            self.app.after(5000, self._execute_ui_pulse_loop)