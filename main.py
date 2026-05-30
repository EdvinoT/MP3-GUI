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

        self.main_frame = ctk.CTkFrame(self, fg_color="#0F051D", corner_radius=0)
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
            print(f"Hardware Log: No image file detected (.jpg, .jpeg, or .png). Using fallback asset color.", flush=True)

        # 2. Typography Header
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="M A I N   M E N U", 
            font=("Futura", 38, "bold"), 
            text_color="#E0AAFF", 
            fg_color="transparent"
        )
        self.title_label.place(relx=0.5, rely=0.15, anchor="center")

        # Active Track Status Bar
        self.status_bar = ctk.CTkLabel(
            self.main_frame, 
            text="▪ NOW PLAYING: IDLE SYSTEM ▪", 
            font=("Futura", 11, "bold"), 
            text_color="#9D4EDD", 
            fg_color="#0A0314",   
            corner_radius=20,
            width=320,
            height=28
        )
        self.status_bar.place(relx=0.5, rely=0.26, anchor="center")

        # 3. Enhanced Navigation Buttons
        button_font = ("Futura", 14, "bold")
        
        self.btn_access = ctk.CTkButton(
            self.main_frame, text="ACCESS SONGS", font=button_font, 
            width=280, height=48, corner_radius=14, 
            fg_color="#1A0933", border_color="#9D4EDD", border_width=1, 
            hover_color="#5A189A", text_color="#E0AAFF", hover_text_color="#FFFFFF",
            command=self.access_songs
        )
        self.btn_access.place(relx=0.5, rely=0.40, anchor="center")

        self.btn_playlist = ctk.CTkButton(
            self.main_frame, text="MAKE A PLAYLIST", font=button_font, 
            width=280, height=48, corner_radius=14, 
            fg_color="#1A0933", border_color="#9D4EDD", border_width=1, 
            hover_color="#5A189A", text_color="#E0AAFF", hover_text_color="#FFFFFF",
            command=self.make_playlist
        )
        self.btn_playlist.place(relx=0.5, rely=0.51, anchor="center")

        self.btn_add = ctk.CTkButton(
            self.main_frame, text="ADD SONG", font=button_font, 
            width=280, height=48, corner_radius=14, 
            fg_color="#1A0933", border_color="#9D4EDD", border_width=1, 
            hover_color="#5A189A", text_color="#E0AAFF", hover_text_color="#FFFFFF",
            command=self.start_download_thread
        )
        self.btn_add.place(relx=0.5, rely=0.62, anchor="center")

        self.btn_off = ctk.CTkButton(
            self.main_frame, text="TURN OFF", font=button_font, 
            width=280, height=48, corner_radius=14, 
            fg_color="#340505", border_color="#FF5555", border_width=1, 
            hover_color="#991B1B", text_color="#FFAAAA", hover_text_color="#FFFFFF",
            command=self.turn_off
        )
        self.btn_off.place(relx=0.5, rely=0.73, anchor="center")

        # Modern Geometric Deck Controls
        self.playback_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.playback_frame.place(relx=0.5, rely=0.88, anchor="center")

        control_font = ("Arial", 16, "bold")

        self.btn_prev = ctk.CTkButton(
            self.playback_frame, text="◀◀", font=control_font, 
            width=55, height=40, corner_radius=10, 
            fg_color="#1A0933", border_color="#9D4EDD", border_width=1, 
            hover_color="#5A189A", text_color="#E0AAFF", hover_text_color="#FFFFFF",
            command=lambda: self.update_status("SKIP BACKWARD")
        )
        self.btn_prev.pack(side="left", padx=12)

        self.btn_play = ctk.CTkButton(
            self.playback_frame, text="▶", font=control_font, 
            width=65, height=40, corner_radius=10, 
            fg_color="#1A0933", border_color="#9D4EDD", border_width=1, 
            hover_color="#5A189A", text_color="#E0AAFF", hover_text_color="#FFFFFF",
            command=lambda: self.update_status("PLAYING TRACK")
        )
        self.btn_play.pack(side="left", padx=12)

        self.btn_next = ctk.CTkButton(
            self.playback_frame, text="▶▶", font=control_font, 
            width=55, height=40, corner_radius=10, 
            fg_color="#1A0933", border_color="#9D4EDD", border_width=1, 
            hover_color="#5A189A", text_color="#E0AAFF", hover_text_color="#FFFFFF",
            command=lambda: self.update_status("SKIP FORWARD")
        )
        self.btn_next.pack(side="left", padx=12)

    # --- Interactive Features ---
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