import customtkinter as ctk
from tkinter import messagebox, Canvas
from PIL import Image, ImageTk
import threading
import time
import os
import warnings
import io

# Mute high-DPI warning logs entirely
warnings.filterwarnings("ignore", category=UserWarning, module="customtkinter")

# Initialize audio engine completely hidden in the background
import pygame
pygame.mixer.init()

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class SurrealPlayerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configurations
        self.title("Surreal Media Player")
        self.geometry("800x600")
        self.resizable(True, True) 

        print("\n=== SYSTEM HARDWARE DIAGNOSTICS ===", flush=True)

        # Core States
        self.track_list = []
        self.current_track_index = 0
        self.is_playing = False

        # Build absolute local paths
        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        self.tracks_dir = os.path.join(self.dir_path, "tracks")
        self.load_local_tracks()

        # FIXED: Enforce a transparent base color palette directly on the layout label widget
        self.bg_label = ctk.CTkLabel(self, text="", fg_color="transparent")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Functional overlay frame for text and buttons
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_frame.place(relwidth=1, relheight=1)

        # Create canvas for background image
        self.bg_canvas = Canvas(self, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_canvas.lower()

        self.bg_photo = None
        self.pil_bg_image = None
        self.resized_bg_image = None

        # Typography Layer
        self.text_title_label = ctk.CTkLabel(
            self.main_frame, text="I D L E   S Y S T E M", 
            font=("Arial", 32), text_color="#FFFFFF", fg_color="transparent"
        )
        self.text_title_label.place(relx=0.5, y=95, anchor="center")

        self.text_sub_label = ctk.CTkLabel(
            self.main_frame, text="▪ ONLINE ▪", 
            font=("Arial", 11), text_color="#666666", fg_color="transparent"
        )
        self.text_sub_label.place(relx=0.5, y=145, anchor="center")

        # Minimalist Options UI Layout
        button_font = ("Futura", 14)
        btn_bg = "#000000" 
        btn_text = "#DDDDDD" 
        btn_hover = "#FFFFFF" 

        self.btn_access = ctk.CTkButton(
            self.main_frame, text="ACCESS SONGS", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            hover_color="#151515", command=self.access_songs
        )
        self.btn_access.place(relx=0.5, rely=0.38, anchor="center")

        self.btn_playlist = ctk.CTkButton(
            self.main_frame, text="MAKE A PLAYLIST", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            hover_color="#151515", command=self.make_playlist
        )
        self.btn_playlist.place(relx=0.5, rely=0.48, anchor="center")

        self.btn_add = ctk.CTkButton(
            self.main_frame, text="ADD SONG", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            hover_color="#151515", command=self.start_download_thread
        )
        self.btn_add.place(relx=0.5, rely=0.58, anchor="center")

        self.btn_off = ctk.CTkButton(
            self.main_frame, text="TURN OFF", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color="#FFAAAA", 
            hover_color="#201010", command=self.turn_off
        )
        self.btn_off.place(relx=0.5, rely=0.68, anchor="center")

        # Audio Deck Controls
        self.playback_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.playback_frame.place(relx=0.5, rely=0.85, anchor="center")

        control_font = ("Arial", 16)

        self.btn_prev = ctk.CTkButton(
            self.playback_frame, text="◀◀", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="#000000", border_width=0, text_color=btn_text,
            hover_color="#151515", command=self.prev_track
        )
        self.btn_prev.pack(side="left", padx=15)

        self.btn_play = ctk.CTkButton(
            self.playback_frame, text="▶", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="#000000", border_width=0, text_color=btn_text,
            hover_color="#151515", command=self.toggle_play
        )
        self.btn_play.pack(side="left", padx=15)

        self.btn_next = ctk.CTkButton(
            self.playback_frame, text="▶▶", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="#000000", border_width=0, text_color=btn_text,
            hover_color="#151515", command=self.next_track
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
        
        # Schedule background setup after window is fully rendered
        self.after(100, self.setup_background_canvas)

    def load_local_tracks(self):
        if not os.path.exists(self.tracks_dir):
            os.makedirs(self.tracks_dir)
        self.track_list = [f for f in os.listdir(self.tracks_dir) if f.endswith(".mp3")]
        self.track_list.sort()
        print(f"Audio Tracks Loaded: {len(self.track_list)} targets inside /tracks folder", flush=True)

    def setup_background_canvas(self):
        png_path = os.path.join(self.dir_path, "background.png")
        print(f"Loading background from: {png_path}", flush=True)
        
        if os.path.exists(png_path):
            try:
                with open(png_path, "rb") as f:
                    image_data = f.read()
                    print(f"Image file size: {len(image_data)} bytes", flush=True)
                
                self.pil_bg_image = Image.open(io.BytesIO(image_data))
                print(f"PIL image loaded: {self.pil_bg_image.size}", flush=True)
                
                # Get current window size
                w = self.winfo_width()
                h = self.winfo_height()
                print(f"Window size: {w}x{h}", flush=True)
                
                # If window not ready, use defaults
                if w <= 1: w = 800
                if h <= 1: h = 600
                
                # Resize image to fit window
                self.resized_bg_image = self.pil_bg_image.resize((w, h), Image.Resampling.LANCZOS)
                print(f"Image resized to: {w}x{h}", flush=True)
                
                # Convert PIL image to PhotoImage for Canvas
                self.bg_photo = ImageTk.PhotoImage(self.resized_bg_image)
                
                # Clear canvas and draw image
                self.bg_canvas.delete("all")
                self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
                self.bg_canvas.config(width=w, height=h)
                print(f"SUCCESS: Background image displayed on canvas at {w}x{h}.", flush=True)
            except Exception as e:
                import traceback
                print(f"Image load error: {e}", flush=True)
                traceback.print_exc()
        else:
            self.bg_canvas.config(bg="#101012")
            print(f"ERROR: background.png not found at {png_path}", flush=True)

    def on_window_resize(self, event):
        if event.widget == self:
            self.setup_background_canvas()

    def update_status_text(self, custom_subtext):
        self.text_sub_label.configure(text=custom_subtext.upper())

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
            self.update_status_text(f"▪ PLAYING: {clean_display_name} ▪")
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