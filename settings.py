import os
import pygame
from PIL import Image, ImageTk

class SettingsMenu:
    def __init__(self, main_app_instance):
        self.app = main_app_instance
        self.active_settings_idx = 0
        
        # Clean menu structure with clear thematic grouping controls
        self.settings_options = [
            "CROSSFADE", 
            "AUDIO FREQ", 
            "SLEEP TIMER", 
            "LED BACKLIGHT", 
            "EQ PRESET",
            "WALLPAPER",      # Cycles images inside your /wallpapers folder
            "THEME: ACCENTS", # Group 1: Changes active menus, underlines, highlights
            "THEME: METRICS", # Group 2: Changes track listings, titles, status logs
            "SAVE CONFIG",
            "LOAD DEFAULTS"
        ]
        self.canvas_settings_ids = []
        
        # Core configuration properties
        self.staged_crossfade = self.app.CROSSFADE_ENABLED
        self.staged_freq = self.app.AUDIO_FREQ
        self.staged_sleep = self.app.SLEEP_MINUTES_LEFT
        self.backlight_level = 80
        self.eq_preset = "FLAT"

        # Expanded Color Palettes for complete UI customization
        self.accent_palette = ["#00A8FF", "#00FF00", "#FFB300", "#FF5555", "#FFFFFF", "#E066FF"]
        self.metric_palette = ["#888888", "#666666", "#A0A0A5", "#555566", "#999999", "#CCCCCC"]
        
        # Set up default configuration indexes if they don't exist yet on main app
        if not hasattr(self.app, 'theme_accent'): self.app.theme_accent = self.accent_palette[0]
        if not hasattr(self.app, 'theme_metric'): self.app.theme_metric = self.metric_palette[0]

        # Scan and index custom wallpapers inside local workspace directory
        self.available_wallpapers = self._scan_for_pngs("wallpapers", fallback="background.png")
        self.wp_idx = 0

        # Premium sleek typography configurations
        self.FONT_TITLE = ("Helvetica Neue", 11, "normal")
        self.FONT_ITEM = ("Helvetica Neue", 10, "normal")
        self.FONT_HIGHLIGHT = ("Helvetica Neue", 10, "underline")

    def _scan_for_pngs(self, folder_name, fallback):
        """Scans the local directory for custom background options."""
        target_dir = os.path.join(self.app.dir_path, folder_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        files = [os.path.join(folder_name, f) for f in os.listdir(target_dir) if f.lower().endswith(".png")]
        return files if files else [fallback]

    def open_settings_scroller(self):
        if self.app.settings_open: return
        self.app.settings_open = True
        
        self.staged_crossfade = self.app.CROSSFADE_ENABLED
        self.staged_freq = self.app.AUDIO_FREQ
        self.staged_sleep = self.app.SLEEP_MINUTES_LEFT
        
        # Hide main app buttons cleanly
        self.app.btn_access.place_forget()
        self.app.btn_shuffle.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_playlist.place_forget()
        self.app.btn_quick_settings.place_forget()
        self.app.btn_off.place_forget()
        
        self.app.playback_frame.place_forget()
        self.app.progress_container.place_forget()
        self.app.controls_dock.place_forget()
        
        if self.app.timer_text_id: self.app.bg_canvas.itemconfig(self.app.timer_text_id, state="hidden")
        if self.app.sleep_text_id: self.app.bg_canvas.itemconfig(self.app.sleep_text_id, state="hidden")
        
        self.app.update_status_text("▪ CONFIGURATION SETTINGS ▪", color=self.app.theme_accent)
        self.refresh_settings_view()

        self.app.bind("<Key-u>", lambda e: self._handle_settings_scroll(-1))
        self.app.bind("<Key-d>", lambda e: self._handle_settings_scroll(1))
        self.app.bind("<Return>", lambda e: self._execute_settings_action())

    def refresh_settings_view(self):
        for cid in self.canvas_settings_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_settings_ids.clear()

        canvas = self.app.bg_canvas

        # Frame mask block
        mask = canvas.create_rectangle(15, 60, 465, 255, fill="#121215", outline="#222228", width=1)
        self.canvas_settings_ids.append(mask)

        # Back / Exit handle
        back_id = canvas.create_text(30, 80, text="◀  EXIT CONFIGURATION", font=self.FONT_TITLE, fill="#FF5555", anchor="w")
        self.canvas_settings_ids.append(back_id)
        canvas.tag_bind(back_id, "<Button-1>", lambda e: self.close_settings_scroller())

        # Clean 3-Column matrix parsing
        for idx, option in enumerate(self.settings_options):
            column = idx // 4  
            row = idx % 4     
            
            x_pos = 30 + (column * 145)
            y_pos = 115 + (row * 34)
            
            if option == "CROSSFADE": status = "ON" if self.staged_crossfade else "OFF"
            elif option == "AUDIO FREQ": status = f"{self.staged_freq//1000}k"
            elif option == "SLEEP TIMER": status = f"{int(self.staged_sleep)}m" if self.staged_sleep > 0 else "OFF"
            elif option == "LED BACKLIGHT": status = f"{self.backlight_level}%"
            elif option == "EQ PRESET": status = self.eq_preset
            elif option == "WALLPAPER": status = os.path.basename(self.available_wallpapers[self.wp_idx])[:8]
            elif option == "THEME: ACCENTS": status = "SWAP"
            elif option == "THEME: METRICS": status = "SWAP"
            elif option in ["SAVE CONFIG", "LOAD DEFAULTS"]: status = "EXEC"
                
            display_text = f"{option}\n[{status}]"
            
            # Apply color highlights depending on what category the configuration option belongs to
            if option == "SAVE CONFIG": fill_color = "#00FF00"
            elif option == "LOAD DEFAULTS": fill_color = "#FF5555"
            elif "THEME" in option or option == "WALLPAPER": fill_color = self.app.theme_accent
            else: fill_color = "#FFFFFF"
            
            text_font = self.FONT_HIGHLIGHT if idx == self.active_settings_idx else self.FONT_ITEM
            
            opt_id = canvas.create_text(x_pos, y_pos, text=display_text, font=text_font, fill=fill_color, anchor="nw")
            self.canvas_settings_ids.append(opt_id)
            
            canvas.tag_bind(opt_id, "<Button-1>", lambda e, i=idx: [self._set_active_idx(i), self._execute_settings_action()])

    def _set_active_idx(self, idx):
        self.active_settings_idx = idx
        self.refresh_settings_view()

    def _handle_settings_scroll(self, direction):
        if hasattr(self.app, 'play_ui_sound'): self.app.play_ui_sound("scroll")
        self.active_settings_idx = (self.active_settings_idx + direction) % len(self.settings_options)
        self.refresh_settings_view()

    def _execute_settings_action(self):
        if hasattr(self.app, 'play_ui_sound'): self.app.play_ui_sound("click")
        selected_option = self.settings_options[self.active_settings_idx]

        if selected_option == "CROSSFADE":
            self.staged_crossfade = not self.staged_crossfade
            
        elif selected_option == "AUDIO FREQ":
            self.staged_freq = 22050 if self.staged_freq == 44100 else 44100
                
        elif selected_option == "SLEEP TIMER":
            self.staged_sleep = 0 if self.staged_sleep >= 60 else self.staged_sleep + 15

        elif selected_option == "LED BACKLIGHT":
            self.backlight_level = 20 if self.backlight_level == 100 else self.backlight_level + 20
            
        elif selected_option == "EQ PRESET":
            presets = ["FLAT", "ROCK", "BASS++", "VOCAL"]
            self.eq_preset = presets[(presets.index(self.eq_preset) + 1) % len(presets)]
            
        elif selected_option == "WALLPAPER":
            self.wp_idx = (self.wp_idx + 1) % len(self.available_wallpapers)
            self._apply_live_wallpaper(self.available_wallpapers[self.wp_idx])

        elif selected_option == "THEME: ACCENTS":
            # Shifts color strings down the accent group array globally
            cur_idx = self.accent_palette.index(self.app.theme_accent)
            self.app.theme_accent = self.accent_palette[(cur_idx + 1) % len(self.accent_palette)]
            self.app.btn_shuffle.configure(text_color=self.app.theme_accent)

        elif selected_option == "THEME: METRICS":
            # Shifts color strings down the metrics group array globally
            cur_idx = self.metric_palette.index(self.app.theme_metric)
            self.app.theme_metric = self.metric_palette[(cur_idx + 1) % len(self.metric_palette)]

        elif selected_option == "SAVE CONFIG":
            self.app.CROSSFADE_ENABLED = self.staged_crossfade
            self.app.SLEEP_MINUTES_LEFT = self.staged_sleep
            if self.app.AUDIO_FREQ != self.staged_freq:
                self.app.AUDIO_FREQ = self.staged_freq
                try:
                    pygame.mixer.quit()
                    pygame.mixer.pre_init(self.app.AUDIO_FREQ, -16, 2, 2048)
                    pygame.mixer.init()
                except Exception: pass
            self.app.update_status_text("▪ CONFIGURATION SAVED ▪", color="#00FF00")

        elif selected_option == "LOAD DEFAULTS":
            self.staged_crossfade = False
            self.staged_freq = 44100
            self.staged_sleep = 0
            self.backlight_level = 80
            self.eq_preset = "FLAT"
            self.wp_idx = 0
            self.app.theme_accent = self.accent_palette[0]
            self.app.theme_metric = self.metric_palette[0]
            self._apply_live_wallpaper("background.png")
            self.app.update_status_text("▪ DEFAULTS LOADED ▪", color="#FFFFFF")
            
        self.refresh_settings_view()

    def _apply_live_wallpaper(self, image_path):
        if not os.path.exists(image_path): return
        try:
            pil_image = Image.open(image_path)
            resized = pil_image.resize((self.app.SCREEN_WIDTH, self.app.SCREEN_HEIGHT), Image.Resampling.NEAREST)
            self.app.bg_photo = ImageTk.PhotoImage(resized)
            self.app.bg_canvas.itemconfig("bg_layer", image=self.app.bg_photo)
        except Exception as e:
            print(f"Error drawing live wallpaper update: {e}")

    def close_settings_scroller(self):
        self.app.settings_open = False
        if hasattr(self.app, 'play_ui_sound'): self.app.play_ui_sound("click")
        
        for cid in self.canvas_settings_ids: self.app.bg_canvas.delete(cid)
        self.canvas_settings_ids.clear()

        self.app.unbind("<Key-u>")
        self.app.unbind("<Key-d>")
        self.app.unbind("<Return>")

        self.app.btn_access.place(x=60, y=140)
        self.app.btn_shuffle.place(x=60, y=190)
        self.app.btn_add.place(x=260, y=140)
        self.app.btn_playlist.place(x=260, y=190)
        self.app.btn_quick_settings.place(x=15, y=266)
        self.app.btn_off.place(x=430, y=266)
        
        self.app.playback_frame.place(relx=0.5, rely=0.82, anchor="center")
        self.app.update_status_text("▪ ONLINE ▪", color=self.app.theme_metric)