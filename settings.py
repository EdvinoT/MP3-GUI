import os
import json
import pygame
from PIL import Image, ImageTk

class SettingsMenu:
    def __init__(self, main_app_instance):
        self.app = main_app_instance
        self.current_page = "MAIN" 
        self.active_settings_idx = 0
        
        self.main_options = [
            "CROSSFADE", 
            "AUDIO FREQ", 
            "SLEEP TIMER", 
            "LED BACKLIGHT", 
            "EQ PRESET",
            "WALLPAPER",        
            "▶ CUSTOMIZE THEME", 
            "SAVE CONFIG",
            "LOAD DEFAULTS"
        ]
        
        self.theme_options = [
            "BOX CARDS",        
            "MENU BUTTONS",     
            "SCROLL TEXT",      
            "SUB HEADINGS",     
            "PLAYLIST UTILS",   
            "◀ BACK TO CONFIG"   
        ]
        
        self.canvas_settings_ids = []
        
        self.staged_crossfade = self.app.CROSSFADE_ENABLED
        self.staged_freq = self.app.AUDIO_FREQ
        self.staged_sleep = self.app.SLEEP_MINUTES_LEFT
        self.backlight_level = 80
        self.eq_preset = "FLAT"

        self.color_spectrum = [
            "#00A8FF", "#00FF00", "#FFB300", "#FF5555", "#FFFFFF", 
            "#E066FF", "#00FFFF", "#FF66B2", "#888888", "#555566"
        ]

        self.available_wallpapers = self._scan_for_pngs("wallpapers", fallback="background.png")
        
        self.wp_idx = 0
        if hasattr(self.app, 'saved_wp'):
            matching_wp = os.path.join("wallpapers", self.app.saved_wp)
            if matching_wp in self.available_wallpapers:
                self.wp_idx = self.available_wallpapers.index(matching_wp)

        self.FONT_TITLE = ("Helvetica Neue", 11, "normal")
        self.FONT_ITEM = ("Helvetica Neue", 10, "normal")
        self.FONT_HIGHLIGHT = ("Helvetica Neue", 10, "underline")

    @property
    def active_options(self):
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
        mask = canvas.create_rectangle(15, 60, 465, 255, fill=self.app.c_box, outline="#44444c", width=1)
        self.canvas_settings_ids.append(mask)

        hdr_text = "◀  EXIT CONFIGURATION" if self.current_page == "MAIN" else "◀  BACK TO SYSTEM CONFIG"
        hdr_fill = "#FF5555" if self.current_page == "MAIN" else self.app.c_play
        
        back_id = canvas.create_text(30, 80, text=hdr_text, font=self.FONT_TITLE, fill=hdr_fill, anchor="w")
        self.canvas_settings_ids.append(back_id)
        
        if self.current_page == "MAIN":
            canvas.tag_bind(back_id, "<Button-1>", lambda e: self.close_settings_scroller())
        else:
            canvas.tag_bind(back_id, "<Button-1>", lambda e: [setattr(self, 'current_page', "MAIN"), setattr(self, 'active_settings_idx', 6), self.refresh_settings_view()])

        for idx, option in enumerate(self.active_options):
            column = idx // 4  
            row = idx % 4     
            
            x_pos = 30 + (column * 145)
            y_pos = 115 + (row * 34)
            
            status = ""
            fill_color = "#FFFFFF"
            
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
                if option == "BOX CARDS": fill_color = self.app.c_box; status = "COLOR"
                elif option == "MENU BUTTONS": fill_color = self.app.c_btn; status = "COLOR"
                elif option == "SCROLL TEXT": fill_color = self.app.c_scroll; status = "COLOR"
                elif option == "SUB HEADINGS": fill_color = self.app.c_sub; status = "COLOR"
                elif option == "PLAYLIST UTILS": fill_color = self.app.c_play; status = "COLOR"
                elif option == "◀ BACK TO CONFIG": fill_color = "#FF5555"

            if self.current_page == "THEME" and fill_color == self.app.c_box:
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
        current_color = getattr(self.app, attribute_name)
        if current_color in self.color_spectrum:
            next_idx = (self.color_spectrum.index(current_color) + 1) % len(self.color_spectrum)
        else:
            next_idx = 0
        setattr(self.app, attribute_name, self.color_spectrum[next_idx])
        self._update_app_button_colors()

    def _execute_settings_action(self):
        if hasattr(self.app, 'play_ui_sound'): self.app.play_ui_sound("click")
        selected_option = self.active_options[self.active_settings_idx]

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
                self.wp_idx = 0
                self.app.c_box, self.app.c_btn, self.app.c_scroll, self.app.c_sub, self.app.c_play = "#121215", "#DDDDDD", "#FFFFFF", "#888888", "#00A8FF"
                self._apply_live_wallpaper("background.png")
                self._update_app_button_colors()
                
                try:
                    if os.path.exists(self.app.config_file):
                        os.remove(self.app.config_file)
                except Exception: pass
                
                self.app.update_status_text("▪ DEFAULTS LOADED ▪", color="#FFFFFF")
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
        """Forces custom tkinter elements and custom module view layers to mirror selected colors."""
        try:
            # Sync root application CTK button widgets
            self.app.btn_access.configure(text_color=self.app.c_btn)
            self.app.btn_shuffle.configure(text_color=self.app.c_btn if not self.app.shuffle_enabled else "#FFB300")
            self.app.btn_add.configure(text_color=self.app.c_btn)
            self.app.btn_playlist.configure(text_color=self.app.c_btn)
            self.app.btn_quick_settings.configure(text_color=self.app.c_btn)
            
            # Sync playback frame infrastructure
            self.app.btn_prev.configure(text_color=self.app.c_btn)
            self.app.btn_play.configure(text_color=self.app.c_btn)
            self.app.btn_next.configure(text_color=self.app.c_btn)
            self.app.progress_bar.configure(fg_color=self.app.c_play)

            # Re-initialize mouse hover listeners to protect new text configurations
            self.app._setup_hover_glow(self.app.btn_access, self.app.c_btn, "#00A8FF")
            self.app._setup_hover_glow(self.app.btn_add, self.app.c_btn, "#00A8FF")
            self.app._setup_hover_glow(self.app.btn_playlist, self.app.c_btn, "#00A8FF")
            self.app._setup_hover_glow(self.app.btn_quick_settings, self.app.c_btn, "#00A8FF")
            self.app._setup_hover_glow(self.app.btn_prev, self.app.c_btn, "#00A8FF")
            self.app._setup_hover_glow(self.app.btn_play, self.app.c_btn, "#00A8FF")
            self.app._setup_hover_glow(self.app.btn_next, self.app.c_btn, "#00A8FF")

            # --- FIX: RECOLOUR THE TICKER MARQUEE AND THE SUBHEAD CANVAS LAYERS LIVE ---
            self.app.bg_canvas.itemconfig("status_sub", fill=self.app.c_sub)
            if hasattr(self.app, 'marquee_color'):
                self.app.marquee_color = self.app.c_sub

            # --- FIX: FORCE RE-COLORING ON CUSTOM EXTERNAL COMPONENT POPUPS & NAVIGATION HEADERS ---
            # Checks for list browser modules
            if hasattr(self.app, 'track_scroller'):
                # Paint scroller navigation headers to c_btn, utility actions to c_play
                self.app.bg_canvas.itemconfig("back_btn", fill=self.app.c_btn)
                self.app.bg_canvas.itemconfig("track_item", fill=self.app.c_scroll)
                if self.app.track_scroller.is_open and hasattr(self.app.track_scroller, 'refresh_scroller_view'):
                    self.app.track_scroller.refresh_scroller_view()
                    
            # Checks for custom playlist modules
            if hasattr(self.app, 'playlist_module'):
                self.app.bg_canvas.itemconfig("playlist_back", fill=self.app.c_btn)
                self.app.bg_canvas.itemconfig("playlist_title", fill=self.app.c_sub)
                self.app.bg_canvas.itemconfig("playlist_util_btn", fill=self.app.c_play) # Groups Create/Edit/Utility actions
                if self.app.playlist_module.is_open and hasattr(self.app.playlist_module, 'refresh_playlist_view'):
                    self.app.playlist_module.refresh_playlist_view()
                    
            # Checks for external injected textbox custom UI frame patches
            if hasattr(self.app, 'custom_textbox_frame'):
                self.app.custom_textbox_frame.configure(fg_color=self.app.c_box)
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
        
        self.app.bg_canvas.tag_raise("main_title")
        self.app.bg_canvas.tag_raise("status_sub")
        self.app.bg_canvas.tag_raise("battery_sub")
        
        self.app.playback_frame.place(relx=0.5, rely=0.82, anchor="center")
        self._update_app_button_colors()
        self.app.update_status_text("▪ ONLINE ▪", color=self.app.c_sub)