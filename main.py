import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import os
import warnings
from PIL import Image, ImageTk, ImageDraw, ImageFont

# Mute CustomTkinter's high-DPI PhotoImage warnings from flooding your terminal profile
warnings.filterwarnings("ignore", category=UserWarning, module="customtkinter")

# Initialize the hardware audio mixer completely independent of the desktop environment
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

        print("Hardware Log: Initializing audio processing layer...", flush=True)

        # Core Playback States
        self.track_list = []
        self.current_track_index = 0
        self.is_playing = False

        # Scan for media targets
        self.dir_path = os.path.dirname(__file__)
        self.tracks_dir = os.path.join(self.dir_path, "tracks")
        self.load_local_tracks()

        # Canvas asset setup using the original, working PhotoImage framework
        self.setup_background_canvas()

        # Transparent Menu Buttons
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

        # Geometric Audio Deck Controls
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

    def load_local_tracks(self):
        if not os.path.exists(self.tracks_dir):
            os.makedirs(self.tracks_dir)
            
        self.track_list = [f for f in os.listdir(self.tracks_dir) if f.endswith(".mp3")]
        self.track_list.sort()
        print(f"Hardware Log: Loaded {len(self.track_list)} track targets.", flush=True)

    def setup_background_canvas(self, custom_subtext="▪ ONLINE ▪"):
        jpeg_path = os.path.join(self.dir_path, "background.jpeg")
        jpg_path = os.path.join(self.dir_path, "background.jpg")
        png_path = os.path.join(self.dir_path, "background.png")
        
        final_image_path = next((p for p in [jpeg_path, jpg_path, png_path] if os.path.exists(p)), None)

        if hasattr(self, 'main_frame'):
            if hasattr(self, 'bg_label'): self.bg_label.destroy()
        else:
            self.main_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
            self.main_frame.pack(fill="both", expand=True)

        if final_image_path:
            try:
                base_img = Image.open(final_image_path).resize((800, 600)).convert("RGBA")
                draw = ImageDraw.Draw(base_img)
                
                try:
                    title_font = ImageFont.truetype("Arial", 32)
                    sub_font = ImageFont.truetype("Arial", 10)
                except IOError:
                    title_font = ImageFont.load_default()
                    sub_font = ImageFont.load_default()
                
                # Write typography directly to your working pixel layer
                draw.text((400, 95), "I D L E   S Y S T E M", fill=(0, 0, 0, 255), font=title_font, anchor="mm")
                draw.text((400, 145), custom_subtext.upper(), fill=(68, 68, 68, 255), font=sub_font, anchor="mm")

                # RESTORED AND FIXED: Standard PhotoImage framework using clean relative layout expansion
                self.bg_photo = ImageTk.PhotoImage(base_img)
                
                self.bg_label = ctk.CTkLabel(self.main_frame, image=self.bg_photo, text="")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1) # Correct placement formatting
                self.bg_label.lower() 
            except Exception as e:
                print(f"Hardware Log: Graphic engine draw failure: {e}", flush=True)
        else:
            self.main_frame.configure(fg_color="#121214")

    def play_current_track(self):
        if not self.track_list:
            return
        
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
            print(f"Hardware Log: Stream execution error: {e}", flush=True)

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