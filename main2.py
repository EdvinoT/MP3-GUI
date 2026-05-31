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
        self.current_playlist = []  
        self.current_track_index = 0
        self.is_playing = False
        self.current_track_length = 0  
        
        self.shuffle_enabled = False
        self.original_order = []    

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
        btn_hover = "#00A8FF"  

        self.btn_access = ctk.CTkButton(
            self, text="ACCESS SONGS", font=button_font, 
            width=160, height=35, corner_radius=4, 
            fg_color=btn_bg, text_color=btn_text,
            command=lambda: [self.play_ui_sound("click"), self.clear_telemetry_for_menu(), self.access_songs()]
        )
        self.btn_access.place(x=60, y=140)

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

        # Main Playback Container (Forced transparent, completely invisible wrapper background)
        self.playback_frame = ctk.CTkFrame(self, fg_color="transparent", bg_color="transparent")
        self.playback_frame.place(relx=0.5, rely=0.82, anchor="center")

        # 1. FLOATING TIMER: 100% transparent background over your main canvas
        self.lbl_timer = ctk.CTkLabel(
            self.playback_frame, text="0:00", 
            fg_color="transparent", bg_color="transparent",
            font=("Courier New", 12, "bold"), text_color="#00A8FF"
        )
        self.lbl_timer.pack(side="top", pady=(0, 4))

        # 2. LINE ANIMATION BOX: This specific container carries the black box background frame
        self.progress_container = ctk.CTkFrame(self.playback_frame, fg_color="#1A1A1A", bg_color="transparent", height=8, width=200, corner_radius=2)
        self.progress_container.pack(side="top", pady=(0, 14)) 
        self.progress_container.pack_propagate(False)

        self.progress_bar = ctk.CTkFrame(self.progress_container, fg_color="#00A8FF", bg_color="transparent", height=8, width=0, corner_radius=2)
        self.progress_bar.pack(side="left")

        # 3. CONTROL BUTTONS DOCK: Separate clean black horizontal container box for the buttons
        self.controls_dock = ctk.CTkFrame(self.playback_frame, fg_color="#1A1A1A", bg_color="transparent", height=36, width=170, corner_radius=4)
        self.controls_dock.pack(side="top")
        self.controls_dock.pack_propagate(False)

        control_font = ("Arial", 12, "bold")

        self.btn_prev = ctk.CTkButton(
            self.controls_dock, text="❬❬", font=control_font, 
            width=35, height=24, fg_color="transparent", text_color=btn_text,
            hover_color="#252525", corner_radius=2,
            command=lambda: [self.play_ui_sound("click"), self.prev_track()]
        )
        self.btn_prev.place(relx=0.2, rely=0.5, anchor="center")

        self.btn_play = ctk.CTkButton(
            self.controls_dock, text="▶", font=control_font, 
            width=40, height=24, fg_color="transparent", text_color=btn_text,
            hover_color="#252525", corner_radius=2,
            command=lambda: [self.play_ui_sound("click"), self.toggle_play()]
        )
        self.btn_play.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_next = ctk.CTkButton(
            self.controls_dock, text="❭❭", font=control_font, 
            width=35, height=24, fg_color="transparent", text_color=btn_text,
            hover_color="#252525", corner_radius=2,
            command=lambda: [self.play_ui_sound("click"), self.next_track()]
        )
        self.btn_next.place(relx=0.8, rely=0.5, anchor="center")

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

        self._update_playback_loop()

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
        
        if getattr(self, 'shuffle_enabled', False):
            random.shuffle(self.track_list)

    def toggle_shuffle(self):
        self.play_ui_sound("click")
        if not self.track_list:
            messagebox.showinfo("Playback", "No tracks available to shuffle.")
            return

        current_track_name = self.track_list[self.current_track_index] if self.track_list else None
        self.shuffle_enabled = not self.shuffle_enabled

        if self.shuffle_enabled:
            random.shuffle(self.track_list)
            self.btn_shuffle.configure(text="SHUFFLE: ON", text_color="#FFB300")
            self.update_status_text("▪ SHUFFLE ENABLED ▪", color="#FFB300")
        else:
            self.track_list = list(self.original_order)
            self.btn_shuffle.configure(text="SHUFFLE: OFF", text_color="#888888")
            self.update_status_text("▪ LINEAR TRACKING ▪", color="#888888")

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
            
            sound_object = pygame.mixer.Sound(track_path)
            self.current_track_length = sound_object.get_length()
            
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
        self.progress_bar.configure(width=0)  
        self.lbl_timer.configure(text="0:00")
        self.current_track_index = (self.current_track_index + 1) % len(self.track_list)
        if self.is_playing:
            self.play_current_track()
        else:
            track_name = self.track_list[self.current_track_index].replace(".mp3", "")
            self.update_status_text(f"{track_name}", color="#888888")

    def prev_track(self):
        if not self.track_list: return
        self.progress_bar.configure(width=0)  
        self.lbl_timer.configure(text="0:00")
        self.current_track_index = (self.current_track_index - 1) % len(self.track_list)
        if self.is_playing:
            self.play_current_track()
        else:
            track_name = self.track_list[self.current_track_index].replace(".mp3", "")
            self.update_status_text(f"{track_name}", color="#888888")

    def _update_playback_loop(self):
        if self.is_playing and self.current_track_length > 0:
            current_ms = pygame.mixer.music.get_pos()
            
            if current_ms == -1 or (pygame.mixer.music.get_busy() == 0 and current_ms > 0):
                self.next_track()
            else:
                current_secs = current_ms / 1000.0
                ratio = min(current_secs / self.current_track_length, 1.0)
                
                self.progress_bar.configure(width=int(ratio * 200))
                
                time_remaining = max(0, int(self.current_track_length - current_secs))
                mins, secs = divmod(time_remaining, 60)
                self.lbl_timer.configure(text=f"{mins}:{secs:02d}")
                
                if time_remaining <= 0:
                    self.next_track()
                    
        elif not self.is_playing:
            if pygame.mixer.music.get_pos() == -1:
                self.progress_bar.configure(width=0)
                self.lbl_timer.configure(text="0:00")

        self.after(200, self._update_playback_loop)

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