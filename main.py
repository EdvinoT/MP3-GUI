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

        print("Hardware Log: Booting media player interface...", flush=True)

        # Look for the background image in the exact same folder as this script
        dir_path = os.path.dirname(__file__)
        jpeg_path = os.path.join(dir_path, "background.jpeg")
        jpg_path = os.path.join(dir_path, "background.jpg")
        
        final_image_path = None
        if os.path.exists(jpeg_path):
            final_image_path = jpeg_path
        elif os.path.exists(jpg_path):
            final_image_path = jpg_path

        # Create the base frame container
        self.main_frame = ctk.CTkFrame(self, fg_color="#0F051D", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        # Attempt to load the background image if found
        if final_image_path:
            print(f"Hardware Log: Found background image at {final_image_path}", flush=True)
            try:
                self.bg_image = Image.open(final_image_path).resize((800, 600))
                self.bg_photo = ImageTk.PhotoImage(self.bg_image)
                
                # Display the image across the entire frame
                self.bg_label = ctk.CTkLabel(self.main_frame, image=self.bg_photo, text="")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Hardware Log: Error loading image: {e}", flush=True)
        else:
            print(f"Hardware Log: No 'background.jpeg' or 'background.jpg' found in {dir_path}. Using solid purple color.", flush=True)

        # Glassmorphic UI layout placed over the background
        button_font = ("Futura", 14, "bold")
        
        self.title_label = ctk.CTkLabel(self.main_frame, text="M A I N   M E N U", font=("Futura", 38, "bold"), text_color="#E0AAFF", fg_color="transparent")
        self.title_label.place(relx=0.5, rely=0.2, anchor="center")

        self.btn_access = ctk.CTkButton(self.main_frame, text="ACCESS SONGS", font=button_font, width=280, height=48, corner_radius=14, fg_color="#1A0933", border_color="#9D4EDD", border_width=1, hover_color="#7B2CBF", text_color="#E0AAFF", command=self.access_songs)
        self.btn_access.place(relx=0.5, rely=0.4, anchor="center")

        self.btn_playlist = ctk.CTkButton(self.main_frame, text="MAKE A PLAYLIST", font=button_font, width=280, height=48, corner_radius=14, fg_color="#1A0933", border_color="#9D4EDD", border_width=1, hover_color="#7B2CBF", text_color="#E0AAFF", command=self.make_playlist)
        self.btn_playlist.place(relx=0.5, rely=0.52, anchor="center")

        self.btn_add = ctk.CTkButton(self.main_frame, text="ADD SONG", font=button_font, width=280, height=48, corner_radius=14, fg_color="#1A0933", border_color="#9D4EDD", border_width=1, hover_color="#7B2CBF", text_color="#E0AAFF", command=self.start_download_thread)
        self.btn_add.place(relx=0.5, rely=0.64, anchor="center")

        self.btn_off = ctk.CTkButton(self.main_frame, text="TURN OFF", font=button_font, width=280, height=48, corner_radius=14, fg_color="#340505", border_color="#FF5555", border_width=1, hover_color="#991B1B", text_color="#FFAAAA", command=self.turn_off)
        self.btn_off.place(relx=0.5, rely=0.78, anchor="center")

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
            
            print("Hardware Log: Track successfully written to target download format (.mp3)", flush=True)
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