import pygame
import loader
import customtkinter as ctk
from tkinter import messagebox, Canvas
from PIL import Image, ImageTk
import threading
import time
import os
import warnings
import io
import scroller
import random 
import battery  

warnings.filterwarnings("ignore", category=UserWarning, module="customtkinter")

try:
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
except Exception as mixer_err:
    print(f"Hardware Mixer Warning: {mixer_err}. Attempting default fallback...")
    pygame.mixer.init()

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class SurrealPlayerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Surreal Media Player")
        self.geometry("800x600")
        self.resizable(True, True) 

        print("\n=== SYSTEM HARDWARE DIAGNOSTICS ===", flush=True)

        self.click_sound = None
        self.scroll_sound = None
        self.shutdown_sound = None
        
        self.ui_channel = pygame.mixer.Channel(0)
        self.load_ui_sounds()

        self.track_list = []
        self.current_playlist = []  
        self.current_track_index = 0
        self.is_playing = False
        
        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        self.tracks_dir = os.path.join(self.dir_path, "tracks")
        
        self.load_local_tracks()

        self.bg_canvas = Canvas(self, highlightthickness=0, bg="#101012")
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.bg_photo = None
        self.pil_bg_image = None
        self.resized_bg_image = None
        
        self.title_text_id = None
        self.sub_text_id = None
        self.battery_text_id = None  

        button_font = ("Futura", 14)
        btn_bg = "#000000" 
        btn_text = "#DDDDDD" 
        btn_hover = "#FFFFFF" 

        self.btn_access = ctk.CTkButton(
            self, text="ACCESS SONGS", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            hover_color="#151515", 
            command=lambda: [self.play_ui_sound("click"), self.access_songs()]
        )
        self.btn_access.place(relx=0.5, rely=0.38, anchor="center")

        self.btn_playlist = ctk.CTkButton(
            self, text="MAKE A PLAYLIST", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            hover_color="#151515", 
            command=lambda: [self.play_ui_sound("click"), self.make_playlist()]
        )
        self.btn_playlist.place(relx=0.5, rely=0.48, anchor="center")

        self.btn_add = ctk.CTkButton(
            self, text="ADD SONG", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            hover_color="#151515", 
            command=lambda: [self.play_ui_sound("click"), loader.SongLoader(self).open_add_song_menu()]
        )
        self.btn_add.place(relx=0.5, rely=0.58, anchor="center")

        self.btn_off = ctk.CTkButton(
            self, text="TURN OFF", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color="#FFAAAA", 
            hover_color="#201010", 
            command=self.turn_off  
        )
        self.btn_off.place(relx=0.5, rely=0.68, anchor="center")

        self.playback_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.playback_frame.place(relx=0.5, rely=0.85, anchor="center")

        control_font = ("Arial", 16)

        self.btn_prev = ctk.CTkButton(
            self.playback_frame, text="◀◀", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="transparent", border_width=0, text_color=btn_text,
            hover_color="#151515", 
            command=lambda: [self.play_ui_sound("click"), self.prev_track()]
        )
        self.btn_prev.pack(side="left", padx=15)

        self.btn_play = ctk.CTkButton(
            self.playback_frame, text="▶", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="transparent", border_width=0, text_color=btn_text,
            hover_color="#151515", 
            command=lambda: [self.play_ui_sound("click"), self.toggle_play()]
        )
        self.btn_play.pack(side="left", padx=15)

        self.btn_next = ctk.CTkButton(
            self.playback_frame, text="▶▶", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="transparent", border_width=0, text_color=btn_text,
            hover_color="#151515", 
            command=lambda: [self.play_ui_sound("click"), self.next_track()]
        )
        self.btn_next.pack(side="left", padx=15)

        self._setup_hover_glow(self.btn_access, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_playlist, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_add, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_off, "#FFAAAA", "#FF5555")
        self._setup_hover_glow(self.btn_prev, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_play, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_next, btn_text, btn_hover)

        self.bind("<Configure>", self.on_window_resize)
        self.after(100, self.setup_background_canvas)
        scroller.TrackScroller(self)

        self.battery_monitor = battery.BatteryTelemetry(self)
        self.battery_monitor.start()

    def load_ui_sounds(self):
        try:
            if os.path.exists("click.ogg"):
                self.click_sound = pygame.mixer.Sound("click.ogg")
            elif os.path.exists("click.wav"):
                self.click_sound = pygame.mixer.Sound("click.wav")

            if os.path.exists("scroll.ogg"):
                self.scroll_sound = pygame.mixer.Sound("scroll.ogg")
            elif os.path.exists("scroll.wav"):
                self.scroll_sound = pygame.mixer.Sound("scroll.wav")

            if os.path.exists("shutdown.wav"):
                self.shutdown_sound = pygame.mixer.Sound("shutdown.wav")
        except Exception as e:
            print(f"Notice: Could not cache audio feedback components: {e}")

    def load_local_tracks(self):
        if not os.path.exists(self.tracks_dir):
            os.makedirs(self.tracks_dir)
        valid_extensions = (".mp3",)
        self.track_list = [f for f in os.listdir(self.tracks_dir) if f.lower().endswith(valid_extensions)]
        self.track_list.sort()
        self.current_playlist = list(self.track_list)

    def setup_background_canvas(self):
        png_path = os.path.join(self.dir_path, "background.png")
        if os.path.exists(png_path):
            try:
                if not self.pil_bg_image:
                    with open(png_path, "rb") as f:
                        image_data = f.read()
                    self.pil_bg_image = Image.open(io.BytesIO(image_data))
                
                w = self.bg_canvas.winfo_width()
                h = self.bg_canvas.winfo_height()
                if w <= 1: w = self.winfo_width()
                if h <= 1: h = self.winfo_height()
                if w <= 1: w = 800
                if h <= 10: h = 600
                
                self.resized_bg_image = self.pil_bg_image.resize((w, h), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(self.resized_bg_image)
                
                self.bg_canvas.delete("all")
                self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
                
                self.title_text_id = self.bg_canvas.create_text(
                    w // 2, 95, text="I D L E   S Y S T E M",
                    font=("Futura", 32), fill="#000000", anchor="center"
                )
                
                current_status = "▪ ONLINE ▪"
                battery_status = "--%"
                if hasattr(self, 'battery_monitor'):
                    current_status = self.battery_monitor.get_status_string()
                    battery_status = f"{self.battery_monitor.current_battery_pct}%"

                self.sub_text_id = self.bg_canvas.create_text(
                    w // 2, 145, text=current_status.upper(),
                    font=("Arial", 11), fill="#BBBBBB", anchor="center"
                )

                self.battery_text_id = self.bg_canvas.create_text(
                    w // 2, 175, text=battery_status,
                    font=("Arial", 10, "bold"), fill="#BBBBBB", anchor="center"
                )
                
                self.bg_canvas.config(scrollregion=self.bg_canvas.bbox("all"))
            except Exception as e:
                print(f"Error loading background canvas: {e}", flush=True)

    def on_window_resize(self, event):
        if event.widget == self:
            if hasattr(self, '_resize_after_id'):
                self.after_cancel(self._resize_after_id)
            self._resize_after_id = self.after(50, self.setup_background_canvas)

    def update_status_text(self, custom_subtext, color="#BBBBBB"):
        if self.sub_text_id is not None:
            self.bg_canvas.itemconfig(self.sub_text_id, text=custom_subtext.upper(), fill=color)

    def update_battery_display(self, text, color="#BBBBBB"):
        if self.battery_text_id is not None:
            self.bg_canvas.itemconfig(self.battery_text_id, text=text, fill=color)

    def play_current_track(self):
        if not self.track_list:
            self.update_status_text("▪ NO SONGS LOADED ▪")
            return
        track_name = self.track_list[self.current_track_index]
        track_path = os.path.join(self.tracks_dir, track_name)
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.btn_play.configure(text="❚❚") 
            if not self.battery_monitor.is_low_battery:
                self.update_status_text(self.battery_monitor.get_status_string())
        except Exception as e:
            self.update_status_text("▪ STREAM ERROR ▪")

    def toggle_play(self):
        if not self.track_list:
            messagebox.showinfo("Storage", "No MP3 entries detected inside the /tracks directory folder.")
            return
        if not self.is_playing:
            if pygame.mixer.music.get_pos() > 0:
                pygame.mixer.music.unpause()
                self.is_playing = True
                self.btn_play.configure(text="❚❚")
                if not self.battery_monitor.is_low_battery:
                    self.update_status_text(self.battery_monitor.get_status_string())
            else:
                self.play_current_track()
        else:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.btn_play.configure(text="▶")
            if not self.battery_monitor.is_low_battery:
                self.update_status_text(self.battery_monitor.get_status_string())

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

    def access_songs(self): pass
    def make_playlist(self): pass

    def turn_off(self):
        """Shutdown logic utilizing safe, isolated conditional layout checks."""
        print("\n=== SYSTEM SHUTDOWN INITIATED ===")
        self.battery_monitor.stop()
        
        self.play_ui_sound("shutdown")
        pygame.mixer.music.stop()

        # CONDITIONAL STATEMENT FOR SHUTDOWN TEXT
        if self.battery_monitor.is_low_battery:
            # Low battery condition: Force dark red layout text
            shutdown_ui_text = "▪ VOLTAGE DROP CRITICAL ▪"
            shutdown_color = "#880000"
            print("[INFO] Flushing core system stack registers...")
        else:
            # Healthy battery condition: Pick a random profile in light gray (#BBBBBB)
            shutdown_profiles = [
                {"log": "Purging audio matrix cache...", "ui": "▪ SYSTEM DE-COMMISSIONED ▪"},
                {"log": "Collapsing local path links...", "ui": "▪ HARDWARE TERMINATED ▪"},
                {"log": "Releasing active app threads...", "ui": "▪ CORE CONSOLE OFFLINE ▪"}
            ]
            chosen = random.choice(shutdown_profiles)
            shutdown_ui_text = chosen["ui"]
            shutdown_color = "#BBBBBB"
            print(f"[INFO] {chosen['log']}")

        print("[INFO] Releasing hardware mixer channels...")
        
        # Apply configurations cleanly
        self.update_status_text(shutdown_ui_text, color=shutdown_color)
        self.update_idletasks() 
        
        self.track_list.clear()
        self.current_playlist.clear()
        time.sleep(0.38)
        
        pygame.mixer.quit()
        print("=== SYSTEM OFFLINE ===\n")
        self.destroy()

    def play_ui_sound(self, sound_type):
        try:
            self.ui_channel.stop()  
            if sound_type == "click" and self.click_sound is not None:
                self.click_sound.set_volume(0.5)  
                self.ui_channel.play(self.click_sound)
            elif sound_type == "scroll" and self.scroll_sound is not None:
                self.scroll_sound.set_volume(0.15)  
                self.ui_channel.play(self.scroll_sound)
            elif sound_type == "shutdown" and hasattr(self, 'shutdown_sound') and self.shutdown_sound is not None:
                self.shutdown_sound.set_volume(0.6)
                self.ui_channel.play(self.shutdown_sound)
        except Exception as e:
            print(f"Audio system feedback error: {e}")

if __name__ == "__main__":
    app = SurrealPlayerApp()
    app.mainloop()