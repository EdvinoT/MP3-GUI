import os
import json
import pygame
from PIL import Image, ImageTk

class SettingsMenu:
    def __init__(self, main_app_instance):
        self.app = main_app_instance
        self.current_page = "MAIN" # Tracks navigation states: "MAIN" or "THEME"
        self.active_settings_idx = 0
        
        # Page 1: Main System Performance Configurations
        self.main_options = [
            "CROSSFADE", 
            "AUDIO FREQ", 
            "SLEEP TIMER", 
            "LED BACKLIGHT", 
            "EQ PRESET",
            "WALLPAPER",        # Cycles files inside /wallpapers/ folder
            "▶ CUSTOMIZE THEME", # Navigates to Page 2
            "SAVE CONFIG",
            "LOAD DEFAULTS"
        ]
        
        # Page 2: Granular Hardware Canvas Theme Builder
        self.theme_options = [
            "BOX CARDS",        # Background frames / popup shapes
            "MENU BUTTONS",     # Main navigation button texts
            "SCROLL TEXT",      # Item text inside the list browser
            "SUB HEADINGS",     # Status headers / tickers / subtitles
            "PLAYLIST UTILS",   # Track editor utility text elements
            "◀ BACK TO CONFIG"   # Navigates back to Page 1
        ]
        
        self.canvas_settings_ids = []
        
        # Local staging cache references
        self.staged_crossfade = self.app.CROSSFADE_ENABLED
        self.staged_freq = self.app.AUDIO_FREQ
        self.staged_sleep = self.app.SLEEP_MINUTES_LEFT
        self.backlight_level = 80
        self.eq_preset = "FLAT"

        # Complete Hardware Color Spectrum Matrix
        self.color_spectrum = [
            "#00A8FF", "#00FF00", "#FFB300", "#FF5555", "#FFFFFF", 
            "#E066FF", "#00FFFF", "#FF66B2", "#888888", "#555566"
        ]

        # Background index mapping setup
        self.available_wallpapers = self._scan_for_pngs("wallpapers", fallback="background.png")
        
        # Sync the wallpaper index pointer with whatever image was loaded from persistent disk memory
        self.wp_idx = 0
        if hasattr(self.app, 'saved_wp'):
            matching_wp = os.path.join("wallpapers", self.app.saved_wp)
            if matching_wp in self.available_wallpapers:
                self.wp_idx = self.available_wallpapers.index(matching_wp)

        # Premium sleek typography configurations
        self.FONT_TITLE = ("Helvetica Neue", 11, "normal")
        self.FONT_ITEM = ("Helvetica Neue", 10, "normal")
        self.FONT_HIGHLIGHT = ("Helvetica Neue", 10, "underline")

    @property
    def active_options(self):
        """Swaps target tracking indexes dynamically based on our active page."""
        return self.main_options if self.current_page == "MAIN" else self.theme_options

    def _scan_for_pngs(self, folder_name, fallback):
        target_dir = os.path.join(self.app.dir_path, folder_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        files = [os.path.join(folder_name, f) for f in os.listdir(target_dir) if f.lower().endswith(".png")]
        return files if files else [fallback]

    def open_settings_scroller(self):
        if self.app.settings_open: return
        self.app.settings_open = True
        self.current_page = "MAIN"
        self.active_settings_idx = 0
        
        self.staged_crossfade = self.app.CROSSFADE_ENABLED
        self.staged_freq = self.app.AUDIO_FREQ
        self.staged_sleep = self.app.SLEEP_MINUTES_LEFT
        
        # Unplace interface controls
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
        
        self.app.update_status_text("▪ CONFIGURATION SETTINGS ▪", color=self.app.c_play)
        self.refresh_settings_view()

        self.app.bind("<Key-u>", lambda e: self._handle_settings_scroll(-1))
        self.app.bind("<Key-d>", lambda e: self._handle_settings_scroll(1))
        self.app.bind("<Return>", lambda e: self._execute_settings_action())

    def refresh_settings_view(self):
        for cid in self.canvas_settings_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_settings_ids.clear()

        canvas = self.app.bg_canvas

        # Background card frame boundary box using our customizable color variables
        mask = canvas.create_rectangle(15, 60, 465, 255, fill=self.app.c_box, outline="#44444c", width=1)
        self.canvas_settings_ids.append(mask)

        # Navigation Header String Line
        hdr_text = "◀  EXIT CONFIGURATION" if self.current_page == "MAIN" else "◀  BACK TO SYSTEM CONFIG"
        hdr_fill = "#FF5555" if self.current_page == "MAIN" else self.app.c_play
        
        back_id = canvas.create_text(30, 80, text=hdr_text, font=self.FONT_TITLE, fill=hdr_fill, anchor="w")
        self.canvas_settings_ids.append(back_id)
        
        if self.current_page == "MAIN":
            canvas.tag_bind(back_id, "<Button-1>", lambda e: self.close_settings_scroller())
        else:
            canvas.tag_bind(back_id, "<Button-1>", lambda e: [setattr(self, 'current_page', "MAIN"), setattr(self, 'active_settings_idx', 6), self.refresh_settings_view()])

        # Build Layout Column Grid Structure Layout
        for idx, option in enumerate(self.active_options):
            column = idx // 4  
            row = idx % 4     
            
            x_pos = 30 + (column * 145)
            y_pos = 115 + (row * 34)
            
            status = ""
            fill_color = "#FFFFFF"
            
            # Context state translation engine logic
            if self.current_page == "MAIN":
                if option == "CROSSFADE": status = "ON" if self.staged_crossfade else "OFF"
                elif option == "AUDIO FREQ": status = f"{self.staged_freq//1000}k"
                elif option == "SLEEP TIMER": status = f"{int(self.staged_sleep)}m" if self.staged_sleep > 0 else "OFF"
                elif option == "LED BACKLIGHT": status = f"{self.backlight_level}%"
                elif option == "EQ PRESET": status = self.eq_preset
                elif option == "WALLPAPER": status = os.path.basename(self.available_wallpapers[self.wp_idx])[:8]
                elif option == "▶ CUSTOMIZE THEME": fill_color = self.app.c_play
                elif option == "SAVE CONFIG": fill_color = "#00FF00"
                elif option == "LOAD DEFAULTS": fill_color = "#FF5555"
            else:
                # Theme customizer value mappings
                if option == "BOX CARDS": fill_color = self.app.c_box; status = "COLOR"
                elif option == "MENU BUTTONS": fill_color = self.app.c_btn; status = "COLOR"
                elif option == "SCROLL TEXT": fill_color = self.app.c_scroll; status = "COLOR"
                elif option == "SUB HEADINGS": fill_color = self.app.c_sub; status = "COLOR"
                elif option == "PLAYLIST UTILS": fill_color = self.app.c_play; status = "COLOR"
                elif option == "◀ BACK TO CONFIG": fill_color = "#FF5555"

            # FIX: If the text color matches the box fill color exactly, give it an outline or fallback shade so it stays visible
            if self.current_page == "THEME" and fill_color == self.app.c_box:
                # Draws a subtle gray guide box behind the text so you can find it
                bg_box = canvas.create_rectangle(x_pos - 4, y_pos - 2, x_pos + 130, y_pos + 28, fill="#1F1F24", outline="#3F3F46", width=1)
                self.canvas_settings_ids.append(bg_box)

            display_text = f"{option}\n[{status}]" if status else option
            text_font = self.FONT_HIGHLIGHT if idx == self.active_settings_idx else self.FONT_ITEM
            
            opt_id = canvas.create_text(x_pos, y_pos, text=display_text, font=text_font, fill=fill_color, anchor="nw")
            self.canvas_settings_ids.append(opt_id)
            
            canvas.tag_bind(opt_id, "<Button-1>", lambda e, i=idx: [self._set_active_idx(i), self._execute_settings_action()])

    def _set_active_idx(self, idx):
        self.active_settings_idx = idx
        self.refresh_settings_view()

    def _handle_settings_scroll(self, direction):
        if hasattr(self.app, 'play_ui_sound'): self.app.play_ui_sound("scroll")
        self.active_settings_idx = (self.active_settings_idx + direction) % len(self.active_options)
        self.refresh_settings_view()

    def _cycle_element_color(self, attribute_name):
        """Cycles a selected color profile variable through our spectrum array."""
        current_color = getattr(self.app, attribute_name)
        if current_color in self.color_spectrum:
            next_idx = (self.color_spectrum.index(current_color) + 1) % len(self.color_spectrum)
        else:
            next_idx = 0
        setattr(self.app, attribute_name, self.color_spectrum[next_idx])

    def _execute_settings_action(self):
        if hasattr(self.app, 'play_ui_sound'): self.app.play_ui_sound("click")
        selected_option = self.active_options[self.active_settings_idx]

        # PAGE 1 Actions Execution Path
        if self.current_page == "MAIN":
            if selected_option == "CROSSFADE": self.staged_crossfade = not self.staged_crossfade
            elif selected_option == "AUDIO FREQ": self.staged_freq = 22050 if self.staged_freq == 44100 else 44100
            elif selected_option == "SLEEP TIMER": self.staged_sleep = 0 if self.staged_sleep >= 60 else self.staged_sleep + 15
            elif selected_option == "LED BACKLIGHT": self.backlight_level = 20 if self.backlight_level == 100 else self.backlight_level + 20
            elif selected_option == "EQ PRESET":
                presets = ["FLAT", "ROCK", "BASS++", "VOCAL"]
                self.eq_preset = presets[(presets.index(self.eq_preset) + 1) % len(presets)]
            elif selected_option == "WALLPAPER":
                self.wp_idx = (self.wp_idx + 1) % len(self.available_wallpapers)
                self._apply_live_wallpaper(self.available_wallpapers[self.wp_idx])
            elif selected_option == "▶ CUSTOMIZE THEME":
                self.current_page = "THEME"
                self.active_settings_idx = 0
            elif selected_option == "SAVE CONFIG":
                self.app.CROSSFADE_ENABLED = self.staged_crossfade
                self.app.SLEEP_MINUTES_LEFT = self.staged_sleep
                
                # Saves persistent data straight to hardware drive via JSON
                config_data = {
                    "c_box": self.app.c_box,
                    "c_btn": self.app.c_btn,
                    "c_scroll": self.app.c_scroll,
                    "c_sub": self.app.c_sub,
                    "c_play": self.app.c_play,
                    "current_wallpaper": os.path.basename(self.available_wallpapers[self.wp_idx])
                }
                try:
                    with open(self.app.config_file, "w") as f:
                        json.dump(config_data, f)
                except Exception as e:
                    print(f"Failed writing hardware settings to SD card: {e}")

                if self.app.AUDIO_FREQ != self.staged_freq:
                    self.app.AUDIO_FREQ = self.staged_freq
                    try:
                        pygame.mixer.quit()
                        pygame.mixer.pre_init(self.app.AUDIO_FREQ, -16, 2, 2048)
                        pygame.mixer.init()
                    except Exception: pass
                
                self._update_app_button_colors()
                self.app.update_status_text("▪ CONFIGURATION SAVED ▪", color="#00FF00")
                
            elif selected_option == "LOAD DEFAULTS":
                self.staged_crossfade = False
                self.staged_freq = 44100
                self.staged_sleep = 0
                self.backlight_level = 80
                self.eq_preset = "FLAT"
                self.wp_idx = 0
                self.app.c_box, self.app.c_btn, self.app.c_scroll, self.app.c_sub, self.app.c_play = "#121215", "#DDDDDD", "#FFFFFF", "#888888", "#00A8FF"
                self._apply_live_wallpaper("background.png")
                self._update_app_button_colors()
                
                try:
                    if os.path.exists(self.app.config_file):
                        os.remove(self.app.config_file)
                except Exception: pass
                
                self.app.update_status_text("▪ DEFAULTS LOADED ▪", color="#FFFFFF")

        # PAGE 2 Theme Actions Execution Path
        else:
            if selected_option == "BOX CARDS": self._cycle_element_color('c_box')
            elif selected_option == "MENU BUTTONS": self._cycle_element_color('c_btn')
            elif selected_option == "SCROLL TEXT": self._cycle_element_color('c_scroll')
            elif selected_option == "SUB HEADINGS": self._cycle_element_color('c_sub')
            elif selected_option == "PLAYLIST UTILS": self._cycle_element_color('c_play')
            elif selected_option == "◀ BACK TO CONFIG":
                self.current_page = "MAIN"
                self.active_settings_idx = 6
                
        self.refresh_settings_view()

    def _update_app_button_colors(self):
        """Forces custom tkinter native button objects to paint themselves to your matching theme color."""
        try:
            # FIX: Force updates both standard text color AND active hover colors to match your theme selections perfectly
            self.app.btn_access.configure(text_color=self.app.c_btn)
            self.app.btn_shuffle.configure(text_color=self.app.c_btn if not self.app.shuffle_enabled else "#FFB300")
            self.app.btn_add.configure(text_color=self.app.c_btn)
            self.app.btn_playlist.configure(text_color=self.app.c_btn)
            self.app.btn_quick_settings.configure(text_color=self.app.c_btn)
            
            # Sync playback frame button components
            self.app.btn_prev.configure(text_color=self.app.c_btn)
            self.app.btn_play.configure(text_color=self.app.c_btn)
            self.app.btn_next.configure(text_color=self.app.c_btn)
            self.app.progress_bar.configure(fg_color=self.app.c_play)

            # Re-bind mouseover listeners to protect new colors during touch interactions
            self.app._setup_hover_glow(self.app.btn_access, self.app.c_btn, "#00A8FF")
            self.app._setup_hover_glow(self.app.btn_add, self.app.c_btn, "#00A8FF")
            self.app._setup_hover_glow(self.app.btn_playlist, self.app.c_btn, "#00A8FF")
            self.app._setup_hover_glow(self.app.btn_quick_settings, self.app.c_btn, "#00A8FF")
            self.app._setup_hover_glow(self.app.btn_prev, self.app.c_btn, "#00A8FF")
            self.app._setup_hover_glow(self.app.btn_play, self.app.c_btn, "#00A8FF")
            self.app._setup_hover_glow(self.app.btn_next, self.app.c_btn, "#00A8FF")
        except Exception as e:
            print(f"UI Color Synchronizer error: {e}")

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
        
        # Layer layout fixes
        self.app.bg_canvas.tag_raise("main_title")
        self.app.bg_canvas.tag_raise("status_sub")
        self.app.bg_canvas.tag_raise("battery_sub")
        
        self.app.playback_frame.place(relx=0.5, rely=0.82, anchor="center")
        self._update_app_button_colors()
        self.app.update_status_text("▪ ONLINE ▪", color=self.app.c_sub)