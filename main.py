import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont

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

        # Completely clear base frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        if final_image_path:
            try:
                # Open image and scale it to layout dimensions
                base_img = Image.open(final_image_path).resize((800, 600)).convert("RGBA")
                
                # Create an editing layer to draw directly onto the image pixels
                draw = ImageDraw.Draw(base_img)
                
                # Try to use a clean default system font, fallback to standard if unavailable
                try:
                    title_font = ImageFont.truetype("Arial", 32)
                    sub_font = ImageFont.truetype("Arial", 10)
                except IOError:
                    title_font = ImageFont.load_default()
                    sub_font = ImageFont.load_default()
                
                # BAKE THE TITLE: Write text directly onto image canvas (Pure Black)
                # Positioned roughly around where the old label sat
                draw.text((400, 95), "I D L E   S Y S T E M", fill=(0, 0, 0, 255), font=title_font, anchor="mm")
                
                # BAKE THE SUB-TRACKER: (Dark Charcoal Gray text)
                draw.text((400, 145), "▪ ONLINE ▪", fill=(68, 68, 68, 255), font=sub_font, anchor="mm")

                # Convert the modified pixel canvas into something Tkinter can display
                self.bg_photo = ImageTk.PhotoImage(base_img)
                self.bg_label = ctk.CTkLabel(self.main_frame, image=self.bg_photo, text="")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                
                print(f"Hardware Log: Successfully baked typography directly into asset: {final_image_path}", flush=True)
            except Exception as e:
                print(f"Hardware Log: Error binding graphic engine layers: {e}", flush=True)
        else:
            self.main_frame.configure(fg_color="#121214")

        # 3. Transparent Menu Controls (Clean light silver text over the lower background area)
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
        print(f"Status Updated: {action_text}", flush=True)

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