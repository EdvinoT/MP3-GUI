import os
import pygame

class SettingsMenu:
    def __init__(self, main_app_instance):
        self.app = main_app_instance
        self.active_settings_idx = 0
        
        # Grid parameters including new Save/Default actions
        self.settings_options = [
            "CROSSFADE", 
            "AUDIO FREQ", 
            "SLEEP TIMER", 
            "LED BACKLIGHT", 
            "EQ PRESET",
            "SAVE CONFIG",
            "LOAD DEFAULTS"
        ]
        self.canvas_settings_ids = []
        
        # Local layout stage cache (staged changes stay blue until committed)
        self.staged_crossfade = self.app.CROSSFADE_ENABLED
        self.staged_freq = self.app.AUDIO_FREQ
        self.staged_sleep = self.app.SLEEP_MINUTES_LEFT
        self.backlight_level = 80
        self.eq_preset = "FLAT"

    def open_settings_scroller(self):
        if self.app.settings_open:
            return
            
        self.app.settings_open = True
        
        # Sync local staging cache with the current app state machine
        self.staged_crossfade = self.app.CROSSFADE_ENABLED
        self.staged_freq = self.app.AUDIO_FREQ
        self.staged_sleep = self.app.SLEEP_MINUTES_LEFT
        
        # Hide main functional and navigation buttons completely
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
            
        if self.app.sleep_text_id:
            self.app.bg_canvas.itemconfig(self.app.sleep_text_id, state="hidden")
        
        self.app.update_status_text("▪ CONFIGURATION SETTINGS ▪", color="#000000")
        self.refresh_settings_view()

        # Key bindings
        self.app.bind("<Key-u>", lambda e: self._handle_settings_scroll(-1))
        self.app.bind("<Key-d>", lambda e: self._handle_settings_scroll(1))
        self.app.bind("<Return>", lambda e: self._execute_settings_action())

    def refresh_settings_view(self):
        for cid in self.canvas_settings_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_settings_ids.clear()

        # Transparent Click Shield
        shield_id = self.app.bg_canvas.create_rectangle(
            0, 0, self.app.SCREEN_WIDTH, self.app.SCREEN_HEIGHT,
            fill="", outline="", tags="settings_shield"
        )
        self.canvas_settings_ids.append(shield_id)
        self.app.bg_canvas.tag_bind(shield_id, "<Button-1>", lambda e: "break")

        # Exit Header 
        back_id = self.app.bg_canvas.create_text(
            25, 130, text="◀  EXIT CONFIGURATION", 
            font=("Courier New", 12, "bold"), fill="#DD2222", anchor="w", tags="settings_back"
        )
        self.canvas_settings_ids.append(back_id)
        self.app.bg_canvas.tag_bind(back_id, "<Button-1>", lambda e: self.close_settings_scroller())

        # Render Multi-Column Adaptive List Layout
        for idx, option in enumerate(self.settings_options):
            column = idx // 4  # Expanded column depth to fit new items
            row = idx % 4     
            
            x_pos = 25 if column == 0 else 245
            y_pos = 162 + (row * 36)
            
            is_changed = False
            
            # Read values straight out of local tracking cache layer
            if option == "CROSSFADE":
                status = "ON (3s)" if self.staged_crossfade else "OFF"
                is_changed = (self.staged_crossfade != self.app.CROSSFADE_ENABLED)
            elif option == "AUDIO FREQ":
                status = f"{self.staged_freq} Hz"
                is_changed = (self.staged_freq != self.app.AUDIO_FREQ)
            elif option == "SLEEP TIMER":
                status = f"{int(self.staged_sleep)}m" if self.staged_sleep > 0 else "OFF"
                is_changed = (self.staged_sleep != self.app.SLEEP_MINUTES_LEFT)
            elif option == "LED BACKLIGHT":
                status = f"{self.backlight_level}%"
            elif option == "EQ PRESET":
                status = self.eq_preset
            elif option in ["SAVE CONFIG", "LOAD DEFAULTS"]:
                status = "ACTION"
                
            display_text = f"{option}\n[{status}]"
            
            # Text coloring engine: modified options stay blue until saved. Functional actions trigger red/green highlights.
            if option == "SAVE CONFIG":
                fill_color = "#008800"  # Soft Green action link
            elif option == "LOAD DEFAULTS":
                fill_color = "#880000"  # Soft Deep Red action link
            else:
                fill_color = "#00A8FF" if is_changed else "#000000"
            
            # Font structural style assignment
            if idx == self.active_settings_idx:
                text_font = ("Courier New", 12, "bold underline")
            else:
                text_font = ("Courier New", 12, "bold")
            
            opt_id = self.app.bg_canvas.create_text(
                x_pos, y_pos, text=display_text, 
                font=text_font, fill=fill_color, anchor="nw", tags="settings_item"
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
            self.staged_crossfade = not self.staged_crossfade
            
        elif selected_option == "AUDIO FREQ":
            if self.staged_freq == 44100: self.staged_freq = 22050
            elif self.staged_freq == 22050: self.staged_freq = 11025
            else: self.staged_freq = 44100
                
        elif selected_option == "SLEEP TIMER":
            # Fixed 15-minute selection loop steps
            if self.staged_sleep == 0: self.staged_sleep = 15
            elif self.staged_sleep == 15: self.staged_sleep = 30
            elif self.staged_sleep == 30: self.staged_sleep = 45
            elif self.staged_sleep == 45: self.staged_sleep = 60
            else: self.staged_sleep = 0

        elif selected_option == "LED BACKLIGHT":
            self.backlight_level = 20 if self.backlight_level == 100 else self.backlight_level + 20
            
        elif selected_option == "EQ PRESET":
            presets = ["FLAT", "ROCK", "BASS++", "VOCAL"]
            next_idx = (presets.index(self.eq_preset) + 1) % len(presets)
            self.eq_preset = presets[next_idx]
            
        elif selected_option == "SAVE CONFIG":
            # Commit staged cache values directly to main application loops
            self.app.CROSSFADE_ENABLED = self.staged_crossfade
            self.app.SLEEP_MINUTES_LEFT = self.staged_sleep
            
            if self.app.AUDIO_FREQ != self.staged_freq:
                self.app.AUDIO_FREQ = self.staged_freq
                try:
                    pygame.mixer.quit()
                    pygame.mixer.pre_init(self.app.AUDIO_FREQ, -16, 2, 2048)
                    pygame.mixer.init()
                except Exception as ex:
                    print(f"[MIXER] Error reloading hardware frequencies: {ex}")
            
            self.app.update_status_text("▪ CONFIGURATION SAVED ▪", color="#000000")

        elif selected_option == "LOAD DEFAULTS":
            # Reset local variables to baseline stock settings
            self.staged_crossfade = False
            self.staged_freq = 44100
            self.staged_sleep = 0
            self.backlight_level = 80
            self.eq_preset = "FLAT"
            self.app.update_status_text("▪ DEFAULTS LOADED ▪", color="#000000")
            
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
        
        if self.app.sleep_text_id:
            self.app.bg_canvas.itemconfig(self.app.sleep_text_id, text="", state="hidden")
        
        self.app.update_status_text("▪ ONLINE ▪", color="#888888")