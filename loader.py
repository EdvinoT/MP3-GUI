import customtkinter as ctk
from tkinter import messagebox, Canvas, filedialog
from PIL import Image, ImageTk
import threading
import time
import os
import warnings
import io
import shutil

# Import yt-dlp safely
try:
    import yt_dlp
except ImportError:
    yt_dlp = None

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
        self.title("Surreal Media Player - V2")
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

        # Create canvas for background image
        self.bg_canvas = Canvas(self, highlightthickness=0, bg="#101012")
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.bg_photo = None
        self.pil_bg_image = None
        self.resized_bg_image = None
        
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

        self.btn_add = ctk.CTkButton(
            self, text="ADD SONG", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            hover_color="#151515", command=self.open_add_song_menu
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
        self.after(100, self.setup_background_canvas)

    def load_local_tracks(self):
        if not os.path.exists(self.tracks_dir):
            os.makedirs(self.tracks_dir)
        self.track_list = [f for f in os.listdir(self.tracks_dir) if f.endswith(".mp3")]
        self.track_list.sort()
        print(f"Audio Tracks Loaded: {len(self.track_list)} targets inside /tracks folder", flush=True)

    def setup_background_canvas(self):
        png_path = os.path.join(self.dir_path, "background.png")
        if os.path.exists(png_path):
            try:
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
                self.sub_text_id = self.bg_canvas.create_text(
                    w // 2, 145, text="▪ ONLINE ▪",
                    font=("Arial", 11), fill="#666666", anchor="center"
                )
                self.bg_canvas.config(scrollregion=self.bg_canvas.bbox("all"))
            except Exception as e:
                print(f"Error loading background canvas: {e}", flush=True)

    def on_window_resize(self, event):
        if event.widget == self:
            self.setup_background_canvas()

    def update_status_text(self, custom_subtext):
        if self.sub_text_id is not None:
            self.bg_canvas.itemconfig(self.sub_text_id, text=custom_subtext.upper())

    # ==========================================
    # DUAL-IMPORT POPUP INTERFACE
    # ==========================================
    def open_add_song_menu(self):
        menu = ctk.CTkToplevel(self)
        menu.title("Add Audio Asset")
        menu.geometry("400x250")
        menu.resizable(False, False)
        menu.transient(self)
        menu.focus_set()
        
        frame = ctk.CTkFrame(menu, fg_color="#101012", corner_radius=0)
        frame.pack(fill="both", expand=True)
        
        lbl = ctk.CTkLabel(frame, text="SELECT TRACK SOURCE", font=("Futura", 16), text_color="#FFFFFF")
        lbl.pack(pady=20)

        btn_local = ctk.CTkButton(
            frame, text="IMPORT FROM LOCAL MAC", font=("Futura", 12),
            width=250, height=35, corner_radius=0, fg_color="#000000",
            text_color="#DDDDDD", hover_color="#151515",
            command=lambda: [menu.destroy(), self.import_local_file()]
        )
        btn_local.pack(pady=10)

        btn_web = ctk.CTkButton(
            frame, text="DOWNLOAD FROM WEB URL", font=("Futura", 12),
            width=250, height=35, corner_radius=0, fg_color="#000000",
            text_color="#DDDDDD", hover_color="#151515",
            command=lambda: [menu.destroy(), self.open_web_download_input()]
        )
        btn_web.pack(pady=10)

    def import_local_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio Track",
            filetypes=[("Audio Files", "*.mp3")]
        )
        if file_path:
            try:
                filename = os.path.basename(file_path)
                destination = os.path.join(self.tracks_dir, filename)
                shutil.copy(file_path, destination)
                
                self.load_local_tracks()
                messagebox.showinfo("Success", f"Imported successfully:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import file: {e}")

    def open_web_download_input(self):
        if yt_dlp is None:
            messagebox.showerror("Missing Module", "Please run 'pip install yt-dlp' in your terminal first.")
            return

        input_win = ctk.CTkToplevel(self)
        input_win.title("Web Stream Fetcher")
        input_win.geometry("450x180")
        input_win.resizable(False, False)
        input_win.transient(self)
        input_win.focus_set()

        frame = ctk.CTkFrame(input_win, fg_color="#101012", corner_radius=0)
        frame.pack(fill="both", expand=True)

        lbl = ctk.CTkLabel(frame, text="PASTE STREAMING AUDIO URL LINK:", font=("Futura", 13), text_color="#FFFFFF")
        lbl.pack(pady=15)

        url_entry = ctk.CTkEntry(frame, width=380, height=30, corner_radius=0, fg_color="#222225", text_color="#FFFFFF", border_width=0)
        url_entry.pack(pady=5)
        url_entry.focus_set()

        btn_download = ctk.CTkButton(
            frame, text="EXECUTE DOWNLOAD PIPELINE", font=("Futura", 12),
            width=200, height=35, corner_radius=0, fg_color="#000000",
            text_color="#DDDDDD", hover_color="#151515",
            command=lambda: self.start_web_download(url_entry.get(), input_win)
        )
        btn_download.pack(pady=15)

    def start_web_download(self, url, window_to_close):
        if not url.strip():
            messagebox.showwarning("Empty Link", "Please insert a valid web URL target link.")
            return
        
        window_to_close.destroy()
        self.btn_add.configure(state="disabled", text="PROCESSING STREAM...")
        
        download_thread = threading.Thread(target=self.download_web_audio_pipeline, args=(url,))
        download_thread.daemon = True
        download_thread.start()

    def download_web_audio_pipeline(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.tracks_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }

        try:
            print(f"Initializing web data extraction sequence for target: {url}", flush=True)
            self.btn_add.configure(text="DOWNLOADING AUDIO...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            print("Web download pipeline completed successfully.", flush=True)
            self.load_local_tracks()
            messagebox.showinfo("Success", "Audio asset downloaded, encoded, and saved to your /tracks playlist bank!")
        except Exception as e:
            print(f"Pipeline failure: {e}", flush=True)
            messagebox.showerror("Error", f"Web extractor could not process this link.\nEnsure link integrity and that ffmpeg is installed.")
        finally:
            self.btn_add.configure(state="normal", text="ADD SONG")

    # ==========================================
    # CORE MEDIA FUNCTIONS
    # ==========================================
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

    def turn_off(self):
        pygame.mixer.quit()
        self.quit()

if __name__ == "__main__":
    app = SurrealPlayerApp()
    app.mainloop()