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
        
        # New hardware stub variables (defaults)
        self.backlight_level = 80
        self.eq_preset = "FLAT"

    def open_settings_scroller(self):
        if self.app.settings_open:
            return
            
        self.app.settings_open = True
        
        # 1. Hide ALL main functional and navigation buttons completely
        self.app.btn_access.place_forget()
        self.app.btn_shuffle.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_playlist.place_forget()
        self.app.btn_quick_settings.place_forget()
        self.app.btn_off.place_forget()
        
        # 2. Clear out the media player tracking frames
        self.app.playback_frame.place_forget()
        self.app.progress_container.place_forget()
        self.app.controls_dock.place_forget()
        
        if self.app.timer_text_id:
            self.app.bg_canvas.itemconfig(self.app.timer_text_id, state="hidden")
        
        self.app.update_status_text("▪ CONFIGURATION SETTINGS ▪", color="#00A8FF")
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

        # FIX: The Transparent Click Shield
        # Creates an invisible rectangle over the entire 480x320 screen space.
        # This swallows all touch/mouse inputs so users cannot click things behind the menu.
        shield_id = self.app.bg_canvas.create_rectangle(
            0, 0, self.app.SCREEN_WIDTH, self.app.SCREEN_HEIGHT,
            fill="", outline="", tags="settings_shield"
        )
        self.canvas_settings_ids.append(shield_id)
        # Bind a do-nothing function to freeze background clicks
        self.app.bg_canvas.tag_bind(shield_id, "<Button-1>", lambda e: "break")

        # Render the Exit Action Header
        back_id = self.app.bg_canvas.create_text(
            25, 130, text="◀  EXIT CONFIGURATION", 
            font=("Futura", 10, "bold"), fill="#FF5555", anchor="w", tags="settings_back"
        )
        self.canvas_settings_ids.append(back_id)
        self.app.bg_canvas.tag_bind(back_id, "<Button-1>", lambda e: self.close_settings_scroller())

        # Render Multi-Column Adaptive List Layout
        # Prevents items from running down into your lower status indicators
        for idx, option in enumerate(self.settings_options):
            # Split items across 2 columns if list grows long
            column = idx // 3  # Columns 0 and 1
            row = idx % 3     # Max 3 rows deep
            
            x_pos = 25 if column == 0 else 250
            y_pos = 165 + (row * 32)
            
            # Read state machines directly from main app or local hardware variables
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
            color = "#00A8FF" if idx == self.active_settings_idx else "#FFFFFF"
            
            opt_id = self.app.bg_canvas.create_text(
                x_pos, y_pos, text=display_text, 
                font=("Arial", 11, "bold"), fill=color, anchor="nw", tags="settings_item"
            )
            self.canvas_settings_ids.append(opt_id)
            
            # Route direct touch events smoothly
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
            # Hook your hardware bridge duty cycle adjustments here later!
            
        elif selected_option == "EQ PRESET":
            presets = ["FLAT", "ROCK", "BASS++", "VOCAL"]
            next_idx = (presets.index(self.eq_preset) + 1) % len(presets)
            self.eq_preset = presets[next_idx]
            
        self.refresh_settings_view()

    def close_settings_scroller(self):
        self.app.settings_open = False
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
        
        # Wipe the click shield and text nodes off the stack
        for cid in self.canvas_settings_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_settings_ids.clear()

        # Drop keyboard capture context
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
        
        # Fire lifecycle controller back up with absolute initialization arguments
        self.app.playback_frame.place(relx=0.5, rely=0.82, anchor="center")
        
        self.app.update_status_text("▪ ONLINE ▪", color="#888888")