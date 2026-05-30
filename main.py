import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
import os
import warnings
from PIL import Image

warnings.filterwarnings("ignore", category=UserWarning, module="customtkinter")

import pygame
pygame.mixer.init()

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class SurrealPlayerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Surreal Media Player")
        self.geometry("800x600")
        self.resizable(False, False) 

        print("\n=== SYSTEM HARDWARE DIAGNOSTICS ===", flush=True)

        self.track_list = []
        self.current_track_index = 0
        self.is_playing = False

        # Force the absolute directory structure of the file itself
        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        print(f"Looking for images inside: {self.dir_path}", flush=True)
        
        self.tracks_dir = os.path.join(self.dir_path, "tracks")
        self.load_local_tracks()

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0, width=800, height=600)
        self.main_frame.pack(fill="both", expand=True)

        self.bg_photo = None
        self.bg_label = None
        self.text_title_label = None
        self.text_sub_label = None

        button_font = ("Futura", 14)
        btn_bg = "transparent"
        btn_text = "#DDDDDD" 
        btn_hover = "#FFFFFF" 

        self.btn_access = ctk.CTkButton(
            self.main_frame, text="ACCESS SONGS", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            bg_color="transparent", command=self.access_songs
        )
        self.btn_access.place(relx=0.5, rely=0.38, anchor="center")

        self.btn_playlist = ctk.CTkButton(
            self.main_frame, text="MAKE A PLAYLIST", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            bg_color="transparent", command=self.make_playlist
        )
        self.btn_playlist.place(relx=0.5, rely=0.48, anchor="center")

        self.btn_add = ctk.CTkButton(
            self.main_frame, text="ADD SONG", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            bg_color="transparent", command=self.start_download_thread
        )
        self.btn_add.place(relx=0.5, rely=0.58, anchor="center")

        self.btn_off = ctk.CTkButton(
            self.main_frame, text="TURN OFF", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color="#FFAAAA", 
            bg_color="transparent", command=self.turn_off
        )
        self.btn_off.place(relx=0.5, rely=0.68, anchor="center")

        self.playback_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.playback_frame.place(relx=0.5, rely=0.85, anchor="center")

        control_font = ("Arial", 16)

        self.btn_prev = ctk.CTkButton(
            self.playback_frame, text="◀◀", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="transparent", border_width=0, text_color=btn_text,
            command=self.prev_track
        )
        self.btn_prev.pack(side="left", padx=15)

        self.btn_play = ctk.CTkButton(
            self.playback_frame, text="▶", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="transparent", border_width=0, text_color=btn_text,
            command=self.toggle_play
        )
        self.btn_play.pack(side="left", padx=15)

        self.btn_next = ctk.CTkButton(
            self.playback_frame, text="▶▶", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="transparent", border_width=0, text_color=btn_text,
            command=self.next_track
        )
        self.btn_next.pack(side="left", padx=15)

        self._setup_hover_glow(self.btn_access, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_playlist, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_add, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_off, "#FFAAAA", "#FF5555")
        self._setup_hover_glow(self.btn_prev, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_play, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_next, btn_text, btn_hover)

        self.setup_background_canvas()

    def load_local_tracks(self):
        if not os.path.exists(self.tracks_dir):
            os.makedirs(self.tracks_dir)
        self.track_list = [f for f in os.listdir(self.tracks_dir) if f.endswith(".mp3")]
        self.track_list.sort()
        print(f"Audio Tracks Loaded: {len(self.track_list)} targets.", flush=True)

    def setup_background_canvas(self, custom_subtext="▪ ONLINE ▪"):
        # Scan for exact casing or alternative matches
        possible_filenames = ["background.png", "Background.png", "background.jpg", "background.jpeg"]
        final_image_path = None
        
        for name in possible_filenames:
            p = os.path.join(self.dir_path, name)
            if os.path.exists(p):
                final_image_path = p
                break

        if self.text_title_label is not None: self.text_title_label.destroy()
        if self.text_sub_label is not None: self.text_sub_label.destroy()

        if self.bg_label is None:
            try:
                if final_image_path:
                    print(f"SUCCESS: Found image asset at {final_image_path}", flush=True)
                    pil_img = Image.open(final_image_path).resize((800, 600)).convert("RGB")
                else:
                    # EMERGENCY FALLBACK: If your file is missing or unreadable, generate a custom neon diagnostic layout
                    print("WARNING: File 'background.png' not found or unreadable! Generating test grid background...", flush=True)
                    pil_img = Image.new("RGB", (800, 600), color=(20, 20, 25))
                    # Draw a distinctive dark grey tech-grid background
                    from PIL import ImageDraw
                    grid_draw = ImageDraw.Draw(pil_img)
                    for x in range(0, 800, 40):
                        grid_draw.line([(x, 0), (x, 600)], fill=(40, 40, 45), width=1)
                    for y in range(0, 600, 40):
                        grid_draw.line([(0, y), (800, y)], fill=(40, 40, 45), width=1)
                
                # Convert the pixel image stream to uncompressed data strings
                ppm_data = f"P6\n800 600\n255\n".encode() + pil_img.tobytes()
                self.bg_photo = tk.PhotoImage(width=800, height=600, data=ppm_data, format="PPM")
                
                self.bg_label = tk.Label(self.main_frame, image=self.bg_photo, bd=0, highlightthickness=0)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_label.lower()
            except Exception as e:
                print(f"Critical Native Rendering Error: {e}", flush=True)

        # Draw typography overlays
        self.text_title_label = ctk.CTkLabel(
            self.main_frame, text="I D L E   S Y S T E M", 
            font=("Arial", 32), text_color="#FFFFFF", fg_color="transparent"
        )
        self.text_title_label.place(relx=0.5, y=95, anchor="center")

        self.text_sub_label = ctk.CTkLabel(
            self.main_frame, text=custom_subtext.upper(), 
            font=("Arial", 10), text_color="#00FFCC", fg_color="transparent"
        )
        self.text_sub_label.place(relx=0.5, y=145, anchor="center")

    def play_current_track(self):
        if not self.track_list: return
        track_name = self.track_list[self.current_track_index]
        track_path = os.path.join(self.tracks_dir, track_name)
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.btn_play.configure(text="❚❚") 
            clean_display_name = track_name.replace(".mp3", "")
            self.setup_background_canvas(custom_subtext=f"▪ PLAYING: {clean_display_name} ▪")
        except Exception as e:
            print(f"Stream execution error: {e}", flush=True)

    def toggle_play(self):
        if not self.track_list:
            messagebox.showinfo("Storage", "No .mp3 file entries detected inside the /tracks directory folder.")
            return
        if not self.is_playing:
            if pygame.mixer.music.get_pos() > 0:
                pygame.mixer.music.unpause()
                self.is_playing = True
                self.btn_play.configure(text="❚❚")
            else:
                self.play_current_track()
        else:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.btn_play.configure(text="▶")

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

    def access_songs(self):
        if self.track_list:
            track_manifest = "\n".join([f"- {t}" for t in self.track_list])
            messagebox.showinfo("Local Index", f"Available Storage Formats:\n\n{track_manifest}")
        else:
            messagebox.showinfo("Local Index", "Storage bank directory empty.")

    def make_playlist(self):
        messagebox.showinfo("Playlist", "Create a new playlist configuration.")

    def start_download_thread(self):
        self.btn_add.configure(state="disabled", text="DOWNLOADING... 0%")
        download_thread = threading.Thread(target=self.simulated_download)
        download_thread.daemon = True 
        download_thread.start()

    def simulated_download(self):
        try:
            for i in range(1, 6):
                time.sleep(0.8) 
                percent = i * 20
                self.btn_add.configure(text=f"DOWNLOADING... {percent}%")
            print("Hardware Log: Track successfully written to target download format (.mp3)", flush=True)
            self.load_local_tracks() 
            messagebox.showinfo("Success", "Audio track saved locally in .mp3 format!")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {str(e)}")
        finally:
            self.btn_add.configure(state="normal", text="ADD SONG")

    def turn_off(self):
        pygame.mixer.quit()
        self.quit()

if __name__ == "__main__":
    app = SurrealPlayerApp()
    app.mainloop()