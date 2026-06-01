import os
import pygame

class SettingsMenu:
    def __init__(self, main_app_instance):
        """
        Manages an overlay configuration console layer on the shared canvas.
        Leaves the main menu title and subtitle visible at the top while cleanly
        hiding ALL menu elements below it.
        """
        self.app = main_app_instance
        self.active_settings_idx = 0
        self.settings_options = ["CROSSFADE", "AUDIO FREQ", "SLEEP TIMER"]
        self.canvas_settings_ids = []

    def open_settings_scroller(self):
        self.app.settings_open = True
        
        # CLEAN FIX: Hide absolutely every button and frame so nothing bleeds through
        self.app.btn_access.place_forget()
        self.app.btn_shuffle.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_settings.place_forget()
        self.app.btn_off.place_forget()  # Hidden cleanly now
        self.app.playback_frame.place_forget()
        
        self.app.update_status_text("▪ CONFIGURATION SETTINGS ▪", color="#00A8FF")
        self.refresh_settings_view()

        # Keyboard emulation hooks for testing dial rotation/clicks
        self.app.bind("<Key-u>", lambda e: self._handle_settings_scroll(-1))
        self.app.bind("<Key-d>", lambda e: self._handle_settings_scroll(1))
        self.app.bind("<Return>", lambda e: self._execute_settings_action())

    def refresh_settings_view(self):
        for cid in self.canvas_settings_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_settings_ids.clear()

        # Transparent alignment: Elements are drawn directly over your original background image
        # Back Menu Text Link
        back_id = self.app.bg_canvas.create_text(
            45, 135, text="◀  EXIT SETTINGS", 
            font=("Futura", 10, "bold"), fill="#FF5555", anchor="w", tags="settings_back"
        )
        self.canvas_settings_ids.append(back_id)
        self.app.bg_canvas.tag_bind(back_id, "<Button-1>", lambda e: self.close_settings_scroller())

        # Render list parameters dynamically onto layout lines
        for idx, option in enumerate(self.settings_options):
            y_pos = 175 + (idx * 35)
            
            if option == "CROSSFADE":
                status = "ON (3s)" if self.app.CROSSFADE_ENABLED else "OFF"
            elif option == "AUDIO FREQ":
                status = f"{self.app.AUDIO_FREQ} Hz"
            elif option == "SLEEP TIMER":
                status = f"{int(self.app.SLEEP_MINUTES_LEFT)}m" if self.app.SLEEP_MINUTES_LEFT > 0 else "OFF"
                
            display_text = f"{option}: {status}"
            color = "#00A8FF" if idx == self.active_settings_idx else "#FFFFFF"
            
            opt_id = self.app.bg_canvas.create_text(
                60, y_pos, text=display_text, font=("Arial", 12, "bold"), fill=color, anchor="w", tags="settings_item"
            )
            self.canvas_settings_ids.append(opt_id)
            
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
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
        selected_option = self.settings_options[self.active_settings_idx]

        if selected_option == "CROSSFADE":
            self.app.CROSSFADE_ENABLED = not self.app.CROSSFADE_ENABLED
            
        elif selected_option == "AUDIO FREQ":
            if self.app.AUDIO_FREQ == 44100: self.app.AUDIO_FREQ = 22050
            elif self.app.AUDIO_FREQ == 22050: self.app.AUDIO_FREQ = 11025
            else: self.app.AUDIO_FREQ = 44100
            
            try:
                pygame.mixer.quit()
                pygame.mixer.pre_init(self.app.AUDIO_FREQ, -16, 2, 2048)
                pygame.mixer.init()
                print(f"[MIXER] Frequency recalibrated to {self.app.AUDIO_FREQ}Hz")
            except Exception as ex:
                print(f"[MIXER] Error reloading rate configuration: {ex}")
                
        elif selected_option == "SLEEP TIMER":
            if self.app.SLEEP_MINUTES_LEFT == 0: self.app.SLEEP_MINUTES_LEFT = 15
            elif self.app.SLEEP_MINUTES_LEFT == 15: self.app.SLEEP_MINUTES_LEFT = 30
            elif self.app.SLEEP_MINUTES_LEFT == 30: self.app.SLEEP_MINUTES_LEFT = 45
            elif self.app.SLEEP_MINUTES_LEFT == 45: self.app.SLEEP_MINUTES_LEFT = 60
            else: self.app.SLEEP_MINUTES_LEFT = 0
            
        self.refresh_settings_view()

    def close_settings_scroller(self):
        self.app.settings_open = False
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
        
        # Clear setting labels from canvas
        for cid in self.canvas_settings_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_settings_ids.clear()

        # Unbind configuration key elements
        self.app.unbind("<Key-u>")
        self.app.unbind("<Key-d>")
        self.app.unbind("<Return>")

        # Restore all widgets back to their clean positions perfectly
        self.app.btn_access.place(x=60, y=140)
        self.app.btn_shuffle.place(x=60, y=190)
        self.app.btn_add.place(x=260, y=140)
        self.app.btn_settings.place(x=260, y=190)
        self.app.btn_off.place(x=15, y=266)  # Restored clean alignment
        self.app.playback_frame.place()
        
        self.app.update_status_text("▪ ONLINE ▪", color="#888888")