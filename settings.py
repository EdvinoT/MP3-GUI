import os
import pygame

class SettingsMenu:
    def __init__(self, main_app_instance):
        """
        Manages an overlay configuration console layer on the shared canvas.
        Optimized to switch crossfade engines, mixer frequencies, and sleep timers.
        """
        self.app = main_app_instance
        self.active_settings_idx = 0
        self.settings_options = ["CROSSFADE", "AUDIO FREQ", "SLEEP TIMER"]
        self.canvas_settings_ids = []

    def open_settings_scroller(self):
        self.app.settings_open = True
        
        # Hide standard menu interface components
        self.app.btn_access.place_forget()
        self.app.btn_shuffle.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_settings.place_forget()
        self.app.btn_off.place_forget()
        self.app.playback_frame.place_forget()
        
        self.app.update_status_text("▪ CONFIGURATION SETTINGS ▪", color="#00A8FF")
        self.refresh_settings_view()

        # Keyboard emulation hooks for testing dial rotation/clicks on your Mac
        self.app.bind("<Key-u>", lambda e: self._handle_settings_scroll(-1))
        self.app.bind("<Key-d>", lambda e: self._handle_settings_scroll(1))
        self.app.bind("<Return>", lambda e: self._execute_settings_action())

    def refresh_settings_view(self):
        import main as m
        for cid in self.canvas_settings_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_settings_ids.clear()

        # Back Menu Text Indicator Button Link
        back_id = self.app.bg_canvas.create_text(
            45, 80, text="◀  EXIT SETTINGS", 
            font=("Futura", 10, "bold"), fill="#FF5555", anchor="w", tags="settings_back"
        )
        self.canvas_settings_ids.append(back_id)
        self.app.bg_canvas.tag_bind(back_id, "<Button-1>", lambda e: self.close_settings_scroller())

        # Render list parameters dynamically onto layout lines
        for idx, option in enumerate(self.settings_options):
            y_pos = 120 + (idx * 35)
            
            # Formulate option state flags strings
            if option == "CROSSFADE":
                status = "ON (3s)" if m.CROSSFADE_ENABLED else "OFF"
            elif option == "AUDIO FREQ":
                status = f"{m.AUDIO_FREQ} Hz"
            elif option == "SLEEP TIMER":
                status = f"{int(m.SLEEP_MINUTES_LEFT)}m" if m.SLEEP_MINUTES_LEFT > 0 else "OFF"
                
            display_text = f"{option}: {status}"
            color = "#00A8FF" if idx == self.active_settings_idx else "#000000"
            
            opt_id = self.app.bg_canvas.create_text(
                60, y_pos, text=display_text, font=("Arial", 12, "bold"), fill=color, anchor="w", tags="settings_item"
            )
            self.canvas_settings_ids.append(opt_id)
            
            # Simple link mouse indexing wrapper to allow click toggles
            self.app.bg_canvas.tag_bind(
                opt_id, 
                "<Button-1>", 
                lambda e, i=idx: [self._set_active_idx(i), self._execute_settings_action()]
            )

    def _set_active_idx(self, idx):
        self.active_settings_idx = idx
        self.refresh_settings_view()

    def _handle_settings_scroll(self, direction):
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("scroll")
        self.active_settings_idx = (self.active_settings_idx + direction) % len(self.settings_options)
        self.refresh_settings_view()

    def _execute_settings_action(self):
        import main as m
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
        selected_option = self.settings_options[self.active_settings_idx]

        if selected_option == "CROSSFADE":
            m.CROSSFADE_ENABLED = not m.CROSSFADE_ENABLED
            
        elif selected_option == "AUDIO FREQ":
            # Rotate target rates between standard profiles
            if m.AUDIO_FREQ == 44100: m.AUDIO_FREQ = 22050
            elif m.AUDIO_FREQ == 22050: m.AUDIO_FREQ = 11025
            else: m.AUDIO_FREQ = 44100
            
            # Reload mixer hardware parameters seamlessly
            try:
                pygame.mixer.quit()
                pygame.mixer.pre_init(m.AUDIO_FREQ, -16, 2, 2048)
                pygame.mixer.init()
                print(f"[MIXER] Frequency recalibrated to {m.AUDIO_FREQ}Hz")
            except Exception as ex:
                print(f"[MIXER] Error reloading rate configuration: {ex}")
                
        elif selected_option == "SLEEP TIMER":
            if m.SLEEP_MINUTES_LEFT == 0: m.SLEEP_MINUTES_LEFT = 15
            elif m.SLEEP_MINUTES_LEFT == 15: m.SLEEP_MINUTES_LEFT = 30
            elif m.SLEEP_MINUTES_LEFT == 30: m.SLEEP_MINUTES_LEFT = 45
            elif m.SLEEP_MINUTES_LEFT == 45: m.SLEEP_MINUTES_LEFT = 60
            else: m.SLEEP_MINUTES_LEFT = 0
            
        self.refresh_settings_view()

    def close_settings_scroller(self):
        self.app.settings_open = False
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
        
        # Clear setting labels from window canvas layers
        for cid in self.canvas_settings_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_settings_ids.clear()

        # Unbind configuration key elements
        self.app.unbind("<Key-u>")
        self.app.unbind("<Key-d>")
        self.app.unbind("<Return>")

        # Restore widgets to original screen coordinates
        self.app.btn_access.place(x=60, y=140)
        self.app.btn_shuffle.place(x=60, y=190)
        self.app.btn_add.place(x=260, y=140)
        self.app.btn_settings.place(x=260, y=190)
        self.app.btn_off.place(x=15, y=266)
        self.app.playback_frame.place()
        
        self.app.update_status_text("▪ ONLINE ▪", color="#888888")