import os
import pygame

class SettingsMenu:
    def __init__(self, main_app_instance):
        self.app = main_app_instance
        self.active_settings_idx = 0
        
        # Expanded menu options to fully utilize the layout profile
        self.settings_options = [
            "CROSSFADE", 
            "AUDIO FREQ", 
            "SLEEP TIMER", 
            "LED BACKLIGHT", 
            "EQ PRESET"
        ]
        self.canvas_settings_ids = []
        
        # Hardware stub variables (defaults)
        self.backlight_level = 80
        self.eq_preset = "FLAT"

    def open_settings_scroller(self):
        if self.app.settings_open:
            return
            
        self.app.settings_open = True
        
        # Hide ALL main functional and navigation buttons completely
        self.app.btn_access.place_forget()
        self.app.btn_shuffle.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_playlist.place_forget()
        self.app.btn_quick_settings.place_forget()
        self.app.btn_off.place_forget()
        
        # Clear out the media player tracking frames
        self.app.playback_frame.place_forget()
        self.app.progress_container.place_forget()
        self.app.controls_dock.place_forget()
        
        if self.app.timer_text_id:
            self.app.bg_canvas.itemconfig(self.app.timer_text_id, state="hidden")
        
        self.app.update_status_text("▪ CONFIGURATION SETTINGS ▪", color="#000000")
        self.refresh_settings_view()

        # Physical hardware key mappings
        self.app.bind("<Key-u>", lambda e: self._handle_settings_scroll(-1))
        self.app.bind("<Key-d>", lambda e: self._handle_settings_scroll(1))
        self.app.bind("<Return>", lambda e: self._execute_settings_action())

    def refresh_settings_view(self):
        # Clean up any previously drawn text elements
        for cid in self.canvas_settings_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_settings_ids.clear()

        # The Transparent Click Shield
        shield_id = self.app.bg_canvas.create_rectangle(
            0, 0, self.app.SCREEN_WIDTH, self.app.SCREEN_HEIGHT,
            fill="", outline="", tags="settings_shield"
        )
        self.canvas_settings_ids.append(shield_id)
        self.app.bg_canvas.tag_bind(shield_id, "<Button-1>", lambda e: "break")

        # Render the Exit Action Header (Changed font to Courier New, color to black)
        back_id = self.app.bg_canvas.create_text(
            25, 130, text="◀  EXIT CONFIGURATION", 
            font=("Courier New", 10, "bold"), fill="#000000", anchor="w", tags="settings_back"
        )
        self.canvas_settings_ids.append(back_id)
        self.app.bg_canvas.tag_bind(back_id, "<Button-1>", lambda e: self.close_settings_scroller())

        # Render Multi-Column Adaptive List Layout
        for idx, option in enumerate(self.settings_options):
            column = idx // 3  
            row = idx % 3     
            
            x_pos = 25 if column == 0 else 250
            y_pos = 165 + (row * 32)
            
            if option == "CROSSFADE":
                status = "ON (3s)" if self.app.CROSSFADE_ENABLED else "OFF"
            elif option == "AUDIO FREQ":
                status = f"{self.app.AUDIO_FREQ} Hz"
            elif option == "SLEEP TIMER":
                status = f"{int(self.app.SLEEP_MINUTES_LEFT)}m" if self.app.SLEEP_MINUTES_LEFT > 0 else "OFF"
            elif option == "LED BACKLIGHT":
                status = f"{self.backlight_level}%"
            elif option == "EQ PRESET":
                status = self.eq_preset
                
            display_text = f"{option}\n{status}"
            
            # Selection UI: Active index gets underlined, but text stays pure black
            text_font = ("Courier New", 10, "bold underline") if idx == self.active_settings_idx else ("Courier New", 10, "bold")
            
            opt_id = self.app.bg_canvas.create_text(
                x_pos, y_pos, text=display_text, 
                font=text_font, fill="#000000", anchor="nw", tags="settings_item"
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
            except Exception as ex:
                print(f"[MIXER] Error reloading hardware frequencies: {ex}")
                
        elif selected_option == "SLEEP TIMER":
            if self.app.SLEEP_MINUTES_LEFT == 0: self.app.SLEEP_MINUTES_LEFT = 15
            elif self.app.SLEEP_MINUTES_LEFT == 15: self.app.SLEEP_MINUTES_LEFT = 30
            elif self.app.SLEEP_MINUTES_LEFT == 30: self.app.SLEEP_MINUTES_LEFT = 45
            elif self.app.SLEEP_MINUTES_LEFT == 45: self.app.SLEEP_MINUTES_LEFT = 60
            else: self.app.SLEEP_MINUTES_LEFT = 0

        elif selected_option == "LED BACKLIGHT":
            self.backlight_level = 20 if self.backlight_level == 100 else self.backlight_level + 20
            
        elif selected_option == "EQ PRESET":
            presets = ["FLAT", "ROCK", "BASS++", "VOCAL"]
            next_idx = (presets.index(self.eq_preset) + 1) % len(presets)
            self.eq_preset = presets[next_idx]
            
        self.refresh_settings_view()

    def close_settings_scroller(self):
        self.app.settings_open = False
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
        
        for cid in self.canvas_settings_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_settings_ids.clear()

        self.app.unbind("<Key-u>")
        self.app.unbind("<Key-d>")
        self.app.unbind("<Return>")

        if hasattr(self.app, 'track_scroller') and self.app.track_scroller.is_open:
            self.app.track_scroller.refresh_scroll_list()
            return

        # Restore main background elements upon exit safely
        self.app.btn_access.place(x=60, y=140)
        self.app.btn_shuffle.place(x=60, y=190)
        self.app.btn_add.place(x=260, y=140)
        self.app.btn_playlist.place(x=260, y=190)
        
        self.app.btn_quick_settings.place(x=15, y=266)
        self.app.btn_off.place(x=430, y=266)
        
        self.app.playback_frame.place(relx=0.5, rely=0.82, anchor="center")
        
        self.app.update_status_text("▪ ONLINE ▪", color="#888888")