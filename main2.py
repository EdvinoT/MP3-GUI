import loader2
import pygame
import customtkinter as ctk
from tkinter import messagebox, Canvas
from PIL import Image, ImageTk
import os
import warnings
import random 
import scroller2  
import battery2  

warnings.filterwarnings("ignore", category=UserWarning, module="customtkinter")

try:
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
except Exception as mixer_err:
    print(f"Hardware Mixer Warning: {mixer_err}")
    try:
        pygame.mixer.init()
    except Exception:
        pass

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class HandheldPlayerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.SCREEN_WIDTH = 480
        self.SCREEN_HEIGHT = 320
        
        self.title("Surreal MP3")
        self.geometry(f"{self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}")
        self.resizable(False, False)  
        
        self.click_sound = None
        self.scroll_sound = None
        self.shutdown_sound = None
        self.ui_channel = pygame.mixer.Channel(0)
        self.load_ui_sounds()

        self.track_list = []
        self.current_playlist = []  # Acts as our active playback queue
        self.current_track_index = 0
        self.is_playing = False
        
        # New Shuffle States
        self.shuffle_enabled = False
        self.original_order = []    # Keeps track of alphabetical order so we can revert

        # Marquee Engine States
        self.marquee_text = "▪ ONLINE ▪"
        self.marquee_job = None
        self.marquee_color = "#888888"
        self.scroll_offset = 0

        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        self.tracks_dir = os.path.join(self.dir_path, "tracks")
        self.load_local_tracks()

        self.bg_canvas = Canvas(self, highlightthickness=0, bg="#101012")
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.bg_photo = None
        self.setup_background_canvas()

        button_font = ("Futura", 11)
        btn_bg = "#1A1A1A" 
        btn_text = "#DDDDDD" 
        btn_hover = "#FFFFFF"

        self.btn_access = ctk.CTkButton(
            self, text="ACCESS SONGS", font=button_font, 
            width=160, height=35, corner_radius=4, 
            fg_color=btn_bg, text_color=btn_text,
            command=lambda: [self.play_ui_sound("click"), self.clear_telemetry_for_menu(), self.access_songs()]
        )
        self.btn_access.place(x=60, y=140)

        # REPLACED PLAYLIST BUTTON WITH SHUFFLE TOGGLE
        self.btn_shuffle = ctk.CTkButton(
            self, text="SHUFFLE: OFF", font=button_font, 
            width=160, height=35, corner_radius=4, 
            fg_color=btn_bg, text_color="#888888",
            command=self.toggle_shuffle
        )
        self.btn_shuffle.place(x=60, y=190)

        self.btn_add = ctk.CTkButton(
            self, text="ADD SONG", font=button_font, 
            width=160, height=35, corner_radius=4, 
            fg_color=btn_bg, text_color=btn_text,
            command=lambda: [self.play_ui_sound("click"), self.clear_telemetry_for_menu(), self.add_song()]
        )
        self.btn_add.place(x=260, y=140)

        self.btn_off = ctk.CTkButton(
            self, text="TURN OFF", font=button_font, 
            width=160, height=35, corner_radius=4, 
            fg_color="#331111", text_color="#FFAAAA", 
            hover_color="#551111",
            command=self.turn_off  
        )
        self.btn_off.place(x=260, y=190)

        self.playback_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.playback_frame.place(relx=0.5, rely=0.85, anchor="center")

        control_font = ("Arial", 14)

        self.btn_prev = ctk.CTkButton(
            self.playback_frame, text="◀◀", font=control_font, 
            width=60, height=35, fg_color=btn_bg, text_color=btn_text,
            command=lambda: [self.play_ui_sound("click"), self.prev_track()]
        )
        self.btn_prev.pack(side="left", padx=10)

        self.btn_play = ctk.CTkButton(
            self.playback_frame, text="▶", font=control_font, 
            width=80, height=35, fg_color=btn_bg, text_color=btn_text,
            command=lambda: [self.play_ui_sound("click"), self.toggle_play()]
        )
        self.btn_play.pack(side="left", padx=10)

        self.btn_next = ctk.CTkButton(
            self.playback_frame, text="▶▶", font=control_font, 
            width=60, height=35, fg_color=btn_bg, text_color=btn_text,
            command=lambda: [self.play_ui_sound("click"), self.next_track()]
        )
        self.btn_next.pack(side="left", padx=10)

        self._setup_hover_glow(self.btn_access, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_add, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_off, "#FFAAAA", "#FF5555")
        self._setup_hover_glow(self.btn_prev, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_play, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_next, btn_text, btn_hover)

        scroller2.TrackScroller(self)
        loader2.SongLoader(self)

        self.battery_monitor = battery2.BatteryTelemetry(self)
        self.battery_monitor.start()

    def load_ui_sounds(self):
        try:
            for ext in ["ogg", "wav"]:
                if os.path.exists(f"click.{ext}"):
                    self.click_sound = pygame.mixer.Sound(f"click.{ext}")
                if os.path.exists(f"scroll.{ext}"):
                    self.scroll_sound = pygame.mixer.Sound(f"scroll.{ext}")
            if os.path.exists("shutdown.wav"):
                self.shutdown_sound = pygame.mixer.Sound("shutdown.wav")
        except Exception as e:
            print(f"Notice: Audio feedback assets unindexed: {e}")

    def load_local_tracks(self):
        if not os.path.exists(self.tracks_dir):
            os.makedirs(self.tracks_dir)
        self.track_list = [f for f in os.listdir(self.tracks_dir) if f.lower().endswith(".mp3")]
        self.track_list.sort()
        self.original_order = list(self.track_list)
        
        # If shuffle was already active when tracks loaded, scramble them
        if getattr(self, 'shuffle_enabled', False):
            random.shuffle(self.track_list)
        else:
            self.track_list = list(self.original_order)

    def toggle_shuffle(self):
        """Switches playback sequence structure between linear and scrambled tracking."""
        self.play_ui_sound("click")
        if not self.track_list:
            messagebox.showinfo("Playback", "No tracks available to shuffle.")
            return

        # Capture whatever track is currently loaded so we don't lose our place
        current_track_name = self.track_list[self.current_track_index] if self.track_list else None

        self.shuffle_enabled = not self.shuffle_enabled

        if self.shuffle_enabled:
            # Scramble the active queue
            random.shuffle(self.track_list)
            self.btn_shuffle.configure(text="SHUFFLE: ON", text_color="#FFB300")
            self.update_status_text("▪ SHUFFLE ENABLED ▪", color="#FFB300")
        else:
            # Revert queue back to alphabetical order
            self.track_list = list(self.original_order)
            self.btn_shuffle.configure(text="SHUFFLE: OFF", text_color="#888888")
            self.update_status_text("▪ LINEAR TRACKING ▪", color="#888888")

        # Re-index to ensure the currently playing song doesn't suddenly jump tracks mid-play
        if current_track_name in self.track_list:
            self.current_track_index = self.track_list.index(current_track_name)

    def setup_background_canvas(self):
        png_path = os.path.join(self.dir_path, "background.png")
        if os.path.exists(png_path):
            try:
                pil_image = Image.open(png_path)
                resized = pil_image.resize((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), Image.Resampling.NEAREST)
                self.bg_photo = ImageTk.PhotoImage(resized)
                self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags="bg_layer")
            except Exception as e:
                print(f"Canvas Image Error: {e}")
        
        self.bg_canvas.create_text(
            self.SCREEN_WIDTH // 2, 45, text="I D L E   S Y S T E M",
            font=("Helvetica Light", 20), fill="#000000", anchor="center", tags="main_title"
        )
        
        self.bg_canvas.create_text(
            self.SCREEN_WIDTH // 2, 85, text="▪ ONLINE ▪",
            font=("Arial", 11), fill="#888888", anchor="center", tags="status_sub"
        )

        self.bg_canvas.create_text(
            self.SCREEN_WIDTH // 2, 110, text="",
            font=("Arial", 9, "bold"), fill="#666666", anchor="center", tags="battery_sub"
        )

    def update_status_text(self, text, color="#888888"):
        if self.marquee_job is not None:
            self.after_cancel(self.marquee_job)
            self.marquee_job = None

        self.marquee_text = text.upper().strip()
        self.marquee_color = color
        self.scroll_offset = 0

        clean_check = self.marquee_text.replace("▶", "").replace("▪", "").strip()
        if len(clean_check) > 16 and "VOLTAGE" not in self.marquee_text and "FLUSH" not in self.marquee_text:
            self._animate_marquee_step()
        else:
            self.bg_canvas.coords("status_sub", self.SCREEN_WIDTH // 2, 85)
            self.bg_canvas.itemconfig("status_sub", text=self.marquee_text, fill=self.marquee_color, anchor="center")

    def _animate_marquee_step(self):
        if self.btn_access.winfo_manager() != "":
            padded_text = self.marquee_text + "         "
            display_string = padded_text[self.scroll_offset:self.scroll_offset + 18]
            
            self.bg_canvas.coords("status_sub", self.SCREEN_WIDTH // 2, 85)
            self.bg_canvas.itemconfig("status_sub", text=display_string, fill=self.marquee_color, anchor="center")
            
            self.scroll_offset = (self.scroll_offset + 1) % len(padded_text)
            self.marquee_job = self.after(280, self._animate_marquee_step)
        else:
            self.marquee_job = None

    def update_battery_display(self, text, color="#666666"):
        if self.btn_access.winfo_manager() != "":
            self.bg_canvas.itemconfig("battery_sub", text=text, fill=color)
        else:
            self.bg_canvas.itemconfig("battery_sub", text="")

    def play_current_track(self):
        if not self.track_list:
            self.update_status_text("▪ NO TRACKS FOUND ▪", color="#FF3333")
            return
        track_name = self.track_list[self.current_track_index]
        track_path = os.path.join(self.tracks_dir, track_name)
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.btn_play.configure(text="❚❚") 
            
            clean_name = track_name.replace(".mp3", "")
            self.update_status_text(f"▶ {clean_name}", color="#FFB300")
        except Exception:
            self.update_status_text("▪ HARDWARE DECODE ERROR ▪", color="#FF3333")

    def toggle_play(self):
        if not self.track_list:
            messagebox.showinfo("Storage", "No MP3 files found in /tracks folder.")
            return
        if not self.is_playing:
            if pygame.mixer.music.get_pos() > 0:
                pygame.mixer.music.unpause()
                self.is_playing = True
                self.btn_play.configure(text="❚❚")
                
                track_name = self.track_list[self.current_track_index].replace(".mp3", "")
                self.update_status_text(f"▶ {track_name}", color="#FFB300")
            else:
                self.play_current_track()
        else:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.btn_play.configure(text="▶")
            self.update_status_text("▪ SYSTEM WAITING ▪", color="#888888")

    def next_track(self):
        if not self.track_list: return
        self.current_track_index = (self.current_track_index + 1) % len(self.track_list)
        self.play_current_track()

    def prev_track(self):
        if not self.track_list: return
        self.current_track_index = (self.current_track_index - 1) % len(self.track_list)
        self.play_current_track()

    def _setup_hover_glow(self, button, normal_color, glow_color):
        button.bind("<Enter>", lambda event: button.configure(text_color=glow_color))
        button.bind("<Leave>", lambda event: button.configure(text_color=normal_color))

    def play_ui_sound(self, sound_type):
        try:
            self.ui_channel.stop()  
            if sound_type == "click" and self.click_sound is not None:
                self.click_sound.set_volume(0.4)  
                self.ui_channel.play(self.click_sound)
            elif sound_type == "scroll" and self.scroll_sound is not None:
                self.scroll_sound.set_volume(0.2)  
                self.ui_channel.play(self.scroll_sound)
            elif sound_type == "shutdown" and self.shutdown_sound is not None:
                self.shutdown_sound.set_volume(0.5)
                self.ui_channel.play(self.shutdown_sound)
        except Exception as e:
            print(f"UI Sound Drop: {e}")

    def clear_telemetry_for_menu(self):
        if self.marquee_job is not None:
            self.after_cancel(self.marquee_job)
            self.marquee_job = None
        self.bg_canvas.itemconfig("battery_sub", text="")
        self.bg_canvas.itemconfig("status_sub", text="")

    def access_songs(self): pass
    def add_song(self): pass

    def return_to_main_menu(self):
        if hasattr(self, 'battery_monitor'):
            self.battery_monitor._process_telemetry_cycle()

    def turn_off(self):
        print("\n=== SYSTEM SHUTDOWN INITIATED ===")
        if self.marquee_job is not None:
            self.after_cancel(self.marquee_job)
            self.marquee_job = None

        self.battery_monitor.stop()
        self.play_ui_sound("shutdown")
        pygame.mixer.music.stop()
        
        self.btn_access.place_forget()
        self.btn_shuffle.place_forget()
        self.btn_add.place_forget()
        self.btn_off.place_forget()
        self.playback_frame.place_forget()
        
        self.bg_canvas.delete("back_btn", "track_item") 

        if self.battery_monitor.current_battery_pct < 20:
            shutdown_ui_text = "▪ VOLTAGE CRITICALY LOW ▪"
            self.update_status_text(shutdown_ui_text, color="#880000")
            self.update()
            self.after(800, self.final_destroy)
        else:
            shutdown_profiles = [
                {"log": "Purging audio matrix cache...", "ui": "▪ SYSTEM DE-COMMISSIONED ▪"},
                {"log": "Collapsing local path links...", "ui": "▪ TERMINATED ▪"},
                {"log": "Releasing active app threads...", "ui": "▪ CORE CONSOLE OFFLINE ▪"},
                {"log": "Terminating the Program...", "ui": "▪ CRITICAL HIT! ▪"}
            ]
            chosen = random.choice(shutdown_profiles)
            print(f"[INFO] {chosen['log']}")
            
            self.update_status_text("▶ INITIALIZING FLUSH COMMANDS...", color="#FFAAAA")
            self.update()
            
            self.after(800, lambda: self.shutdown_step_two(chosen["ui"]))

    def shutdown_step_two(self, secondary_text):
        self.update_status_text(secondary_text, color="#BBBBBB")
        self.update()
        self.after(800, self.final_destroy)

    def final_destroy(self):
        self.track_list.clear()
        self.current_playlist.clear()
        pygame.mixer.quit()
        print("=== SYSTEM OFFLINE ===\n")
        self.destroy()

if __name__ == "__main__":
    app = HandheldPlayerApp()
    app.mainloop()