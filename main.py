import loader
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
        self.current_playlist = []  # FIXED: Initialized BEFORE calling load_local_tracks()
        self.current_track_index = 0
        self.is_playing = False

        # Build absolute local paths
        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        self.tracks_dir = os.path.join(self.dir_path, "tracks")
        
        # Now it is completely safe to load your tracks!
        self.load_local_tracks()

        # Create canvas for background image
        self.bg_canvas = Canvas(self, highlightthickness=0, bg="#101012")
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.bg_photo = None
        self.pil_bg_image = None
        self.resized_bg_image = None
        
        # Canvas item ID tracking variables for dynamic redraw events
        self.title_text_id = None
        self.sub_text_id = None

        # Minimalist Options UI Layout
        button_font = ("Futura", 14)
        btn_bg = "#000000" 
        btn_text = "#DDDDDD" 
        btn_hover = "#FFFFFF" 

        self.btn_access = ctk.CTkButton(
            self, text="ACCESS SONGS", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            hover_color="#151515", command=self.access_songs
        )
        self.btn_access.place(relx=0.5, rely=0.38, anchor="center")

        self.btn_playlist = ctk.CTkButton(
            self, text="MAKE A PLAYLIST", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            hover_color="#151515", command=self.make_playlist
        )
        self.btn_playlist.place(relx=0.5, rely=0.48, anchor="center")

        # Spawning a clean background instance of the loader to process the menu assets securely
        self.btn_add = ctk.CTkButton(
            self, text="ADD SONG", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            hover_color="#151515", 
            command=lambda: loader.SongLoader(self).open_add_song_menu()
        )
        self.btn_add.place(relx=0.5, rely=0.58, anchor="center")

        self.btn_off = ctk.CTkButton(
            self, text="TURN OFF", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color="#FFAAAA", 
            hover_color="#201010", command=self.turn_off
        )
        self.btn_off.place(relx=0.5, rely=0.68, anchor="center")

        # Audio Deck Controls
        self.playback_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.playback_frame.place(relx=0.5, rely=0.85, anchor="center")

        control_font = ("Arial", 16)

        self.btn_prev = ctk.CTkButton(
            self.playback_frame, text="◀◀", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="transparent", border_width=0, text_color=btn_text,
            hover_color="#151515", command=self.prev_track
        )
        self.btn_prev.pack(side="left", padx=15)

        self.btn_play = ctk.CTkButton(
            self.playback_frame, text="▶", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="transparent", border_width=0, text_color=btn_text,
            hover_color="#151515", command=self.toggle_play
        )
        self.btn_play.pack(side="left", padx=15)

        self.btn_next = ctk.CTkButton(
            self.playback_frame, text="▶▶", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="transparent", border_width=0, text_color=btn_text,
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
        
        # Accept multiple standard audio extensions that Pygame can play
        valid_extensions = (".mp3", ".m4a", ".wav", ".ogg", ".webm")
        self.track_list = [f for f in os.listdir(self.tracks_dir) if f.lower().endswith(valid_extensions)]
        self.track_list.sort()
        
        if not self.current_playlist:
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
                
                # Clear all canvas content to draw a fresh frame
                self.bg_canvas.delete("all")
                
                # Layer 1: Render background image structure
                self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
                
                # Layer 2: Draw typography strings natively on the canvas
                self.title_text_id = self.bg_canvas.create_text(
                    w // 2, 95, text="I D L E   S Y S T E M",
                    font=("Futura", 32), fill="#000000", anchor="center"
                )
                
                # Dynamically set subtext status depending on playback state
                current_status = "▪ ONLINE ▪"
                if self.is_playing and self.track_list:
                    clean_name = self.track_list[self.current_track_index]
                    for ext in (".mp3", ".m4a", ".wav", ".ogg", ".webm"):
                        clean_name = clean_name.replace(ext, "")
                    current_status = f"▪ PLAYING: {clean_name} ▪"

                self.sub_text_id = self.bg_canvas.create_text(
                    w // 2, 145, text=current_status.upper(),
                    font=("Arial", 11), fill="#666666", anchor="center"
                )
                
                self.bg_canvas.config(scrollregion=self.bg_canvas.bbox("all"))
            except Exception as e:
                print(f"Error loading background canvas: {e}", flush=True)
        else:
            self.bg_canvas.delete("all")
            w = self.winfo_width()
            self.title_text_id = self.bg_canvas.create_text(w // 2, 95, text="I D L E   S Y S T E M", font=("Futura", 32), fill="#FFFFFF")

    def on_window_resize(self, event):
        if event.widget == self:
            # Debounce window resizing using Tkinter's 'after' helper to optimize frame processing performance
            if hasattr(self, '_resize_after_id'):
                self.after_cancel(self._resize_after_id)
            self._resize_after_id = self.after(50, self.setup_background_canvas)

    def update_status_text(self, custom_subtext):
        if self.sub_text_id is not None:
            self.bg_canvas.itemconfig(self.sub_text_id, text=custom_subtext.upper())

    def play_current_track(self):
        if not self.track_list:
            return

        # FIXED: Pulling the actual track name strings dynamically from the track list
        track_name = self.track_list[self.current_track_index]
        track_path = os.path.join(self.tracks_dir, track_name)

        # Replaces any of our extensions cleanly for screen display
        clean_display_name = track_name
        for ext in (".mp3", ".m4a", ".wav", ".ogg", ".webm"):
            clean_display_name = clean_display_name.replace(ext, "")
        
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.btn_play.configure(text="❚❚") 
            self.update_status_text(f"▪ PLAYING: {clean_display_name} ▪")
        except Exception as e:
            print(f"Stream execution error: {e}", flush=True)
            self.update_status_text("▪ STREAM ERROR ▪")

    def toggle_play(self):
        if not self.track_list:
            messagebox.showinfo("Storage", "No media entries detected inside the /tracks directory folder.")
            return
        if not self.is_playing:
            if pygame.mixer.music.get_pos() > 0:
                pygame.mixer.music.unpause()
                self.is_playing = True
                self.btn_play.configure(text="❚❚")
                
                track_name = self.track_list[self.current_track_index]
                for ext in (".mp3", ".m4a", ".wav", ".ogg", ".webm"):
                    track_name = track_name.replace(ext, "")
                self.update_status_text(f"▪ PLAYING: {track_name} ▪")
            else:
                self.play_current_track()
        else:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.btn_play.configure(text="▶")
            self.update_status_text("▪ PAUSED ▪")

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
        self.destroy() # FIXED: closes down window contexts cleanly without letting tasks hang

if __name__ == "__main__":
    app = SurrealPlayerApp()
    app.mainloop()