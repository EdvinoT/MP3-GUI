import loader2
import pygame
import customtkinter as ctk
from tkinter import messagebox, Canvas
from PIL import Image, ImageTk
import os
import warnings
import io
import random 
import scroller2  

# Hide unnecessary warnings on the small screen
warnings.filterwarnings("ignore", category=UserWarning, module="customtkinter")

# Initialize hardware mixer with a safe fallback for the Pi Zero
try:
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
except Exception as mixer_err:
    print(f"Hardware Mixer Warning: {mixer_err}. Using default fallback...")
    try:
        pygame.mixer.init()
    except Exception:
        print("Audio hardware detached or unavailable.")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class HandheldPlayerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. FIXED HANDHELD DIMENSIONS (Perfect for a 3.5" or 2.8" screen)
        self.SCREEN_WIDTH = 480
        self.SCREEN_HEIGHT = 320
        
        self.title("Surreal MP3")
        self.geometry(f"{self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}")
        self.resizable(False, False)  
        
        # Track Management
        self.track_list = []
        self.current_track_index = 0
        self.is_playing = False
        
        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        self.tracks_dir = os.path.join(self.dir_path, "tracks")
        self.load_local_tracks()

        # UI Canvas for Background & Text
        self.bg_canvas = Canvas(self, highlightthickness=0, bg="#101012")
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Load the background image statically (no heavy CPU resizing)
        self.setup_background_canvas()

        # 2. COMPACT BUTTON LAYOUT
        button_font = ("Futura", 11)
        btn_bg = "#1A1A1A" 
        btn_text = "#DDDDDD" 

        # Left Column Buttons
        self.btn_access = ctk.CTkButton(
            self, text="ACCESS SONGS", font=button_font, 
            width=160, height=35, corner_radius=4, 
            fg_color=btn_bg, text_color=btn_text,
            command=self.access_songs
        )
        self.btn_access.place(x=60, y=140)

        self.btn_playlist = ctk.CTkButton(
            self, text="PLAYLISTS", font=button_font, 
            width=160, height=35, corner_radius=4, 
            fg_color=btn_bg, text_color=btn_text,
            command=self.make_playlist
        )
        self.btn_playlist.place(x=60, y=190)

        # Right Column Buttons
        self.btn_add = ctk.CTkButton(
            self, text="ADD SONG", font=button_font, 
            width=160, height=35, corner_radius=4, 
            fg_color=btn_bg, text_color=btn_text,
            command=self.add_song
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

        # 3. LOWERED PLAYBACK CONTROLS
        self.playback_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.playback_frame.place(relx=0.5, rely=0.85, anchor="center")

        control_font = ("Arial", 14)

        self.btn_prev = ctk.CTkButton(
            self.playback_frame, text="◀◀", font=control_font, 
            width=60, height=35, fg_color=btn_bg, text_color=btn_text,
            command=self.prev_track
        )
        self.btn_prev.pack(side="left", padx=10)

        self.btn_play = ctk.CTkButton(
            self.playback_frame, text="▶", font=control_font, 
            width=80, height=35, fg_color=btn_bg, text_color=btn_text,
            command=self.toggle_play
        )
        self.btn_play.pack(side="left", padx=10)

        self.btn_next = ctk.CTkButton(
            self.playback_frame, text="▶▶", font=control_font, 
            width=60, height=35, fg_color=btn_bg, text_color=btn_text,
            command=self.next_track
        )
        self.btn_next.pack(side="left", padx=10)

        # Load modules
        scroller2.TrackScroller(self)
        loader2.SongLoader(self)

    def load_local_tracks(self):
        if not os.path.exists(self.tracks_dir):
            os.makedirs(self.tracks_dir)
        self.track_list = [f for f in os.listdir(self.tracks_dir) if f.lower().endswith(".mp3")]
        self.track_list.sort()

    def setup_background_canvas(self):
        """Loads image statically to protect the Pi Zero CPU from lag spikes."""
        png_path = os.path.join(self.dir_path, "background.png")
        if os.path.exists(png_path):
            try:
                self.pil_bg_image = Image.open(png_path)
                resized = self.pil_bg_image.resize((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), Image.Resampling.NEAREST)
                self.bg_photo = ImageTk.PhotoImage(resized)
                self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            except Exception as e:
                print(f"Canvas Image Error: {e}")
        
        # Primary Title Header
        self.title_text_id = self.bg_canvas.create_text(
            self.SCREEN_WIDTH // 2, 45, text="I D L E   S Y S T E M",
            font=("Helvetica Light", 20), fill="#000000", anchor="center"
        )
        
        # Dynamic Status / Track Readout Line
        self.sub_text_id = self.bg_canvas.create_text(
            self.SCREEN_WIDTH // 2, 85, text="▪ ONLINE ▪",
            font=("Arial", 11), fill="#888888", anchor="center"
        )

    def update_status_text(self, text, color="#888888"):
        if hasattr(self, 'sub_text_id') and self.sub_text_id is not None:
            self.bg_canvas.itemconfig(self.sub_text_id, text=text.upper(), fill=color)

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
            
            # Clean track title representation for the header block
            clean_name = track_name.replace(".mp3", "")
            display_name = clean_name if len(clean_name) < 24 else clean_name[:21] + "..."
            
            self.bg_canvas.itemconfig(self.title_text_id, text="N O W   P L A Y I N G", fill="#000000")
            self.update_status_text(f"▶ {display_name}", color="#00FF00")
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
                display_name = track_name if len(track_name) < 24 else track_name[:21] + "..."
                self.bg_canvas.itemconfig(self.title_text_id, text="N O W   P L A Y I N G", fill="#000000")
                self.update_status_text(f"▶ {display_name}", color="#00FF00")
            else:
                self.play_current_track()
        else:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.btn_play.configure(text="▶")
            self.bg_canvas.itemconfig(self.title_text_id, text="P A U S E D", fill="#000000")
            self.update_status_text("▪ SYSTEM WAITING ▪", color="#888888")

    def next_track(self):
        if not self.track_list: return
        self.current_track_index = (self.current_track_index + 1) % len(self.track_list)
        self.play_current_track()

    def prev_track(self):
        if not self.track_list: return
        self.current_track_index = (self.current_track_index - 1) % len(self.track_list)
        self.play_current_track()

    def access_songs(self): pass
    def make_playlist(self): pass
    def add_song(self): pass

    def turn_off(self):
        """Executes a sequenced terminal-style shutdown script layout on the canvas screen."""
        # 1. Kill active hardware tasks safely
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        
        # 2. Dismiss physical button panels to isolate background text blocks
        self.btn_access.place_forget()
        self.btn_playlist.place_forget()
        self.btn_add.place_forget()
        self.btn_off.place_forget()
        self.playback_frame.place_forget()
        
        # 3. Restyle headers into terminal feedback logs
        self.bg_canvas.itemconfig(self.title_text_id, text="S H U T D O W N", fill="#FF5555")
        self.update_status_text("▶ TERMINATING SYSTEM PROCESSES...", color="#FFAAAA")
        self.update_idletasks()
        
        # Low-overhead delay steps to allow the user to read logs without locked frame rendering
        self.after(400, lambda: self.shutdown_step_two())

    def shutdown_step_two(self):
        """Appends the secondary line update to the hardware console prompt."""
        self.update_status_text("▶ UNMOUNTING CORE AUDIO ENGINE...", color="#FFAAAA")
        self.update_idletasks()
        self.after(400, lambda: self.shutdown_step_three())

    def shutdown_step_three(self):
        """Displays final structural status before terminating application loop lifecycle."""
        self.update_status_text("▶ POWER CORES OFFLINE.", color="#FF3333")
        self.update_idletasks()
        self.after(500, lambda: self.destroy())

if __name__ == "__main__":
    app = HandheldPlayerApp()
    app.mainloop()