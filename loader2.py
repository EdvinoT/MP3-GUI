import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import os
import shutil

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

class SongLoader:
    def __init__(self, main_app_instance):
        self.app = main_app_instance
        self.tracks_dir = main_app_instance.tracks_dir
        
        # Link the ADD SONG button on the main app directly to this module
        self.app.btn_add.configure(command=self.open_add_song_menu)

    def open_add_song_menu(self):
        """Spawns an elegant minimalist modal window perfectly sized for a handheld."""
        menu = ctk.CTkToplevel(self.app)
        menu.title("Add Audio Asset")
        
        # Sized to take up a compact portion of the 480x320 screen
        menu.geometry("320x180")
        menu.resizable(False, False)
        menu.configure(fg_color="#101012")
        menu.transient(self.app)
        menu.focus_set()
        
        # Position cleanly inside the handheld window frame boundaries
        menu.update_idletasks()
        x = self.app.winfo_x() + (self.app.SCREEN_WIDTH // 2) - (320 // 2)
        y = self.app.winfo_y() + (self.app.SCREEN_HEIGHT // 2) - (180 // 2)
        menu.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(menu, fg_color="#101012", corner_radius=0)
        frame.pack(fill="both", expand=True)
        
        # Spaced out text styling matching the IDLE SYSTEM look
        lbl = ctk.CTkLabel(frame, text="S E L E C T   S O U R C E", font=("Helvetica Light", 13), text_color="#FFFFFF")
        lbl.pack(pady=15)

        btn_local = ctk.CTkButton(
            frame, text="IMPORT FROM LOCAL STORAGE", font=("Futura", 10),
            width=240, height=32, corner_radius=0, fg_color="#000000",
            text_color="#DDDDDD", hover_color="#151515",
            command=lambda: [menu.destroy(), self.import_local_file()]
        )
        btn_local.pack(pady=8)

        btn_web = ctk.CTkButton(
            frame, text="DOWNLOAD FROM WEB URL", font=("Futura", 10),
            width=240, height=32, corner_radius=0, fg_color="#000000",
            text_color="#DDDDDD", hover_color="#151515",
            command=lambda: [menu.destroy(), self.open_web_download_input()]
        )
        btn_web.pack(pady=8)

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
                
                self.app.load_local_tracks()
                self.app.bg_canvas.delete("all")
                self.app.setup_background_canvas()
                
                messagebox.showinfo("Success", f"Imported successfully:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import file: {e}")

    def open_web_download_input(self):
        if yt_dlp is None:
            messagebox.showerror("Missing Module", "Please run 'pip install yt-dlp' in your terminal first.")
            return

        input_win = ctk.CTkToplevel(self.app)
        input_win.title("Web Stream Fetcher")
        input_win.geometry("360x150")
        input_win.resizable(False, False)
        input_win.configure(fg_color="#101012")
        input_win.transient(self.app)
        input_win.focus_set()

        input_win.update_idletasks()
        x = self.app.winfo_x() + (self.app.SCREEN_WIDTH // 2) - (360 // 2)
        y = self.app.winfo_y() + (self.app.SCREEN_HEIGHT // 2) - (150 // 2)
        input_win.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(input_win, fg_color="#101012", corner_radius=0)
        frame.pack(fill="both", expand=True)

        lbl = ctk.CTkLabel(frame, text="PASTE STREAMING AUDIO URL LINK:", font=("Futura", 11), text_color="#FFFFFF")
        lbl.pack(pady=12)

        url_entry = ctk.CTkEntry(frame, width=320, height=28, corner_radius=0, fg_color="#222225", text_color="#FFFFFF", border_width=0)
        url_entry.pack(pady=2)
        url_entry.focus_set()

        btn_download = ctk.CTkButton(
            frame, text="EXECUTE DOWNLOAD PIPELINE", font=("Futura", 11),
            width=220, height=32, corner_radius=0, fg_color="#000000",
            text_color="#DDDDDD", hover_color="#151515",
            command=lambda: self.start_web_download(url_entry.get(), input_win)
        )
        btn_download.pack(pady=12)

    def start_web_download(self, url, window_to_close):
        if not url.strip():
            messagebox.showwarning("Empty Link", "Please insert a valid web URL target link.")
            return
        
        window_to_close.destroy()
        self.app.btn_add.configure(state="disabled", text="PROCESSING STREAM...")
        
        download_thread = threading.Thread(target=self.download_web_audio_pipeline, args=(url,))
        download_thread.daemon = True
        download_thread.start()

    def download_web_audio_pipeline(self, url):
        project_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_bin_path = os.path.join(project_dir, "ffmpeg")

        ydl_opts = {
            'noplaylist': True,
            'format': 'bestaudio/best',
            'extract_flat': False,
            'nocheckcertificate': True,
            'outtmpl': os.path.join(self.tracks_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': ffmpeg_bin_path, 
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            self.app.btn_add.configure(text="DOWNLOADING...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.app.load_local_tracks()
            self.app.bg_canvas.delete("all")
            self.app.setup_background_canvas()
            
            messagebox.showinfo("Success", "Audio track saved successfully!")
        except Exception as e:
            print(f"Download error details: {e}")
            messagebox.showerror(
                "Conversion Error", 
                "Web download pipeline failed.\n\nPlease ensure 'ffmpeg' is sitting inside your project folder."
            )
        finally:
            self.app.btn_add.configure(state="normal", text="ADD SONG")