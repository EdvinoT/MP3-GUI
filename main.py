import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import sys

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class SurrealPlayerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Surreal Media Player")
        
        # MAC FORCE-REFRESH FIX: We allow resizing but manage drawing explicitly
        self.geometry("800x600")
        self.resizable(True, True) 

        # Main background frame
        self.main_frame = ctk.CTkFrame(self, fg_color="#0F051D", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, text="MAIN MENU", 
            font=("Segoe UI", 36, "bold"), text_color="#D6A4FF"
        )
        self.title_label.pack(pady=(100, 40))

        # Separator
        self.separator = ctk.CTkFrame(self.main_frame, height=2, width=200, fg_color="#3A1C5C")
        self.separator.pack(pady=(0, 40))

        # Buttons
        self.btn_access = ctk.CTkButton(
            self.main_frame, text="ACCESS SONGS", font=("Segoe UI", 14, "bold"),
            width=260, height=45, corner_radius=8, fg_color="#240B36",
            hover_color="#5A189A", text_color="#E0AAFF", command=self.access_songs
        )
        self.btn_access.pack(pady=10)

        self.btn_playlist = ctk.CTkButton(
            self.main_frame, text="MAKE A PLAYLIST", font=("Segoe UI", 14, "bold"),
            width=260, height=45, corner_radius=8, fg_color="#240B36",
            hover_color="#5A189A", text_color="#E0AAFF", command=self.make_playlist
        )
        self.btn_playlist.pack(pady=10)

        self.btn_add = ctk.CTkButton(
            self.main_frame, text="ADD SONG", font=("Segoe UI", 14, "bold"),
            width=260, height=45, corner_radius=8, fg_color="#240B36",
            hover_color="#5A189A", text_color="#E0AAFF", command=self.start_download_thread
        )
        self.btn_add.pack(pady=10)

        self.btn_off = ctk.CTkButton(
            self.main_frame, text="TURN OFF", font=("Segoe UI", 14, "bold"),
            width=260, height=45, corner_radius=8, fg_color="#450A0A",
            hover_color="#991B1B", text_color="#FFAAAA", command=self.turn_off
        )
        self.btn_off.pack(pady=30)

        # Force a rendering engine kickstart specifically for macOS environments
        self.after(100, self.kickstart_mac_render)

    def kickstart_mac_render(self):
        """Forces the window engine to cycle frame states, breaking the blank loop."""
        self.update()
        self.geometry("801x601")  # Shift by 1 pixel to shock the window manager into drawing
        self.update()
        self.geometry("800x600")  # Set back to original layout target

    def access_songs(self):
        messagebox.showinfo("Library", "Opening local storage music library.")

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
            
            print("Hardware Log: Track successfully written to /home/pi/Music/track.mp3")
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