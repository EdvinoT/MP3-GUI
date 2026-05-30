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
        # Tie the loader directly to your main app context
        self.app = main_app_instance
        self.tracks_dir = main_app_instance.tracks_dir

    def open_add_song_menu(self):
        """Spawns an elegant minimalist modal window over the main app window."""
        menu = ctk.CTkToplevel(self.app)
        menu.title("Add Audio Asset")
        menu.geometry("400x220")
        menu.resizable(False, False)
        menu.configure(fg_color="#101012")
        menu.transient(self.app)
        menu.focus_set()
        
        # Center the popup over the main application window
        menu.update_idletasks()
        x = self.app.winfo_x() + (self.app.winfo_width() // 2) - (400 // 2)
        y = self.app.winfo_y() + (self.app.winfo_height() // 2) - (220 // 2)
        menu.geometry(f"+{x}+{y}")
        
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
                
                self.app.load_local_tracks()
                messagebox.showinfo("Success", f"Imported successfully:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import file: {e}")

    def open_web_download_input(self):
        if yt_dlp is None:
            messagebox.showerror("Missing Module", "Please run 'pip install yt-dlp' in your terminal first.")
            return

        input_win = ctk.CTkToplevel(self.app)
        input_win.title("Web Stream Fetcher")
        input_win.geometry("450x180")
        input_win.resizable(False, False)
        input_win.configure(fg_color="#101012")
        input_win.transient(self.app)
        input_win.focus_set()

        # Center this window too
        input_win.update_idletasks()
        x = self.app.winfo_x() + (self.app.winfo_width() // 2) - (450 // 2)
        y = self.app.winfo_y() + (self.app.winfo_height() // 2) - (180 // 2)
        input_win.geometry(f"+{x}+{y}")

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
        self.app.btn_add.configure(state="disabled", text="PROCESSING STREAM...")
        
        download_thread = threading.Thread(target=self.download_web_audio_pipeline, args=(url,))
        download_thread.daemon = True
        download_thread.start()

    def download_web_audio_pipeline(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'nocheckcertificate': True,  # <-- ADD THIS LINE TO BYPASS THE SSL ERROR
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
            self.app.btn_add.configure(text="DOWNLOADING AUDIO...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.app.load_local_tracks()
            messagebox.showinfo("Success", "Audio asset saved to your playlist bank!")
        except Exception as e:
            print(f"Download error details: {e}")
            messagebox.showerror("Error", f"Web extractor pipeline failure.\nEnsure link integrity or check FFmpeg.")
        finally:
            self.app.btn_add.configure(state="normal", text="ADD SONG")