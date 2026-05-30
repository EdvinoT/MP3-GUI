import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import os
from PIL import Image, ImageTk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class SurrealPlayerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Surreal Media Player")
        self.geometry("800x600")
        self.resizable(False, False) 

        print("Hardware Log: Booting universally compatible media player...", flush=True)

        # 1. Background Setup (Accepts .jpeg, .jpg, and .png)
        dir_path = os.path.dirname(__file__)
        jpeg_path = os.path.join(dir_path, "background.jpeg")
        jpg_path = os.path.join(dir_path, "background.jpg")
        png_path = os.path.join(dir_path, "background.png")
        
        final_image_path = None
        if os.path.exists(jpeg_path):
            final_image_path = jpeg_path
        elif os.path.exists(jpg_path):
            final_image_path = jpg_path
        elif os.path.exists(png_path):
            final_image_path = png_path

        # Completely clear base frame to prevent purple bleed
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        if final_image_path:
            try:
                self.bg_image = Image.open(final_image_path).resize((800, 600))
                self.bg_photo = ImageTk.PhotoImage(self.bg_image)
                self.bg_label = ctk.CTkLabel(self.main_frame, image=self.bg_photo, text="")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                print(f"Hardware Log: Successfully loaded background asset from {final_image_path}", flush=True)
            except Exception as e:
                print(f"Hardware Log: Error loading image framework: {e}", flush=True)
        else:
            # Simple dark slate gray fallback if no image is present
            self.main_frame.configure(fg_color="#121214")

        # 2. Sleek Minimal Typography Header (Melts into image)
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="M A I N   M E N U", 
            font=("Futura", 36, "normal"), 
            text_color="#FFFFFF", # Crisp white to pop off any dark image
            fg_color="transparent"
        )
        self.title_label.place(relx=0.5, rely=0.15, anchor="center")

        # Minimal Status Bar (Completely transparent background, just clean text tracking)
        self.status_bar = ctk.CTkLabel(
            self.main_frame, 
            text="▪ IDLE SYSTEM ▪", 
            font=("Futura", 11), 
            text_color="#AAAAAA", # Subdued light gray
            fg_color="transparent"
        )
        self.status_bar.place(relx=0.5, rely=0.24, anchor="center")

        # 3. Transparent Floating Menu Controls
        button_font = ("Futura", 14)
        
        # We use a very faint dark tint with NO borders so the background image shows right through the buttons
        btn_bg = "transparent"
        btn_text = "#DDDDDD"
        btn_hover = "#FFFFFF"

        self.btn_access = ctk.CTkButton(
            self.main_frame, text="ACCESS SONGS", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            command=self.access_songs
        )
        self.btn_access.place(relx=0.5, rely=0.38, anchor="center")

        self.btn_playlist = ctk.CTkButton(
            self.main_frame, text="MAKE A PLAYLIST", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            command=self.make_playlist
        )
        self.btn_playlist.place(relx=0.5, rely=0.48, anchor="center")

        self.btn_add = ctk.CTkButton(
            self.main_frame, text="ADD SONG", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color=btn_text,
            command=self.start_download_thread
        )
        self.btn_add.place(relx=0.5, rely=0.58, anchor="center")

        self.btn_off = ctk.CTkButton(
            self.main_frame, text="TURN OFF", font=button_font, 
            width=280, height=45, corner_radius=0, 
            fg_color=btn_bg, border_width=0, text_color="#FFAAAA", # Soft red hue for the exit trigger
            command=self.turn_off
        )
        self.btn_off.place(relx=0.5, rely=0.68, anchor="center")

        # Geometric Audio Deck Controls (Stripped down to minimal transparent icons)
        self.playback_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.playback_frame.place(relx=0.5, rely=0.85, anchor="center")

        control_font = ("Arial", 16)

        self.btn_prev = ctk.CTkButton(
            self.playback_frame, text="◀◀", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="transparent", border_width=0, text_color=btn_text,
            command=lambda: self.update_status("SKIP BACKWARD")
        )
        self.btn_prev.pack(side="left", padx=15)

        self.btn_play = ctk.CTkButton(
            self.playback_frame, text="▶", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="transparent", border_width=0, text_color=btn_text,
            command=lambda: self.update_status("PLAYING TRACK")
        )
        self.btn_play.pack(side="left", padx=15)

        self.btn_next = ctk.CTkButton(
            self.playback_frame, text="▶▶", font=control_font, 
            width=50, height=40, corner_radius=0, 
            fg_color="transparent", border_width=0, text_color=btn_text,
            command=lambda: self.update_status("SKIP FORWARD")
        )
        self.btn_next.pack(side="left", padx=15)

        # Connect dynamic hover brightness bindings
        self._setup_hover_glow(self.btn_access, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_playlist, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_add, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_off, "#FFAAAA", "#FF5555")
        self._setup_hover_glow(self.btn_prev, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_play, btn_text, btn_hover)
        self._setup_hover_glow(self.btn_next, btn_text, btn_hover)

    # --- Interactive Features ---
    def _setup_hover_glow(self, button, normal_color, glow_color):
        button.bind("<Enter>", lambda event: button.configure(text_color=glow_color))
        button.bind("<Leave>", lambda event: button.configure(text_color=normal_color))

    def update_status(self, action_text):
        self.status_bar.configure(text=f"▪ {action_text} ▪")

    def access_songs(self):
        self.update_status("ACCESSING STORAGE")
        messagebox.showinfo("Library", "Opening local storage music library.")

    def make_playlist(self):
        self.update_status("PLAYLIST CONFIG MODE")
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
                self.status_bar.configure(text=f"▪ DOWNLOADING DATA: {percent}% ▪")
            
            print("Hardware Log: Track successfully written to target download format (.mp3)", flush=True)
            self.status_bar.configure(text="▪ DOWNLOAD COMPLETE ▪")
            messagebox.showinfo("Success", "Audio track saved locally in .mp3 format!")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {str(e)}")
        finally:
            self.btn_add.configure(state="normal", text="ADD SONG")

    def turn_off(self):
        self.quit()

if __name__ == "__main__":
    app = SurrealPlayerApp()
    app.mainloop()