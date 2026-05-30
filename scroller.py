import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import os

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Takes the main app instance so this separate module can hijack
        the ACCESS SONGS button and inject a flawless translucent overlay.
        """
        self.app = main_app_instance
        self.is_open = False  
        self.scroll_frame = None
        self.nav_frame = None

        # Overwrite the default button command in main.py to trigger our custom view toggle
        self.app.btn_access.configure(command=self.toggle_full_page_scroller)

        # Intercept the track-loading system to update our scroller if it's currently open
        self.original_load_tracks = self.app.load_local_tracks
        self.app.load_local_tracks = self.wrapped_load_local_tracks

    def toggle_full_page_scroller(self):
        """Toggles the full screen track archive menu view on and off."""
        if not self.is_open:
            self.open_full_page_scroller()
        else:
            self.close_full_page_scroller()

    def open_full_page_scroller(self):
        """Alters the background image to add an isolated translucent text box panel."""
        self.is_open = True
        
        # 1. Hide the main operational menu buttons (Leave lower controls alone)
        self.app.btn_access.place_forget()
        self.app.btn_playlist.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_off.place_forget()

        # 2. Render a true light alpha-channel translucent glass box panel directly onto the canvas pixels
        if self.app.pil_bg_image:
            w = self.app.bg_canvas.winfo_width()
            h = self.app.bg_canvas.winfo_height()
            
            base_img = self.app.pil_bg_image.resize((w, h), Image.Resampling.LANCZOS).convert("RGBA")
            
            overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # FIXED: Drastically lowered the alpha opacity value (from 180 down to 110)
            # This makes the panel heavily translucent so your background image easily shines through!
            draw.rectangle(
                [int(w * 0.05), int(h * 0.12), int(w * 0.95), int(h * 0.82)], 
                fill=(5, 5, 10, 110),
                outline=(40, 40, 50, 150),
                width=1
            )
            
            final_tinted_image = Image.alpha_composite(base_img, overlay)
            
            self.app.bg_photo = ImageTk.PhotoImage(final_tinted_image)
            self.app.bg_canvas.delete("all")
            self.app.bg_canvas.create_image(0, 0, image=self.app.bg_photo, anchor="nw")

        # 3. Create a transparent container for our navigation return controller
        self.nav_frame = ctk.CTkFrame(self.app, height=60, fg_color="transparent")
        self.nav_frame.place(relx=0, rely=0, relwidth=1, anchor="nw")

        btn_back = ctk.CTkButton(
            self.nav_frame, text="◀  BACK TO MENU", font=("Futura", 12),
            width=140, height=35, corner_radius=0,
            fg_color="#000000", text_color="#DDDDDD", hover_color="#151515",
            command=self.close_full_page_scroller
        )
        btn_back.pack(side="left", padx=20, pady=12)

        # 4. Spawn the giant scrolling track frame inside our transparent window area
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.app, 
            fg_color="transparent", 
            corner_radius=0, 
            border_width=0
        )
        self.scroll_frame.place(relx=0.06, rely=0.14, relwidth=0.88, relheight=0.66)

        self.refresh_scroll_list()

    def close_full_page_scroller(self):
        """Destroys the scroll list view cleanly and drops you straight back to the main menu."""
        self.is_open = False

        # Destroy the layout tracking components entirely
        if self.scroll_frame is not None:
            self.scroll_frame.destroy()
            self.scroll_frame = None
        if self.nav_frame is not None:
            self.nav_frame.destroy()
            self.nav_frame = None

        # Command the main hub to instantly recalculate and paint its default background image
        self.app.setup_background_canvas()

        # Bring back your home selection menu options exactly where they belong
        self.app.btn_access.place(relx=0.5, rely=0.38, anchor="center")
        self.app.btn_playlist.place(relx=0.5, rely=0.48, anchor="center")
        self.app.btn_add.place(relx=0.5, rely=0.58, anchor="center")
        self.app.btn_off.place(relx=0.5, rely=0.68, anchor="center")

        # CRITICAL RE-RENDER PATCH: Forces the Mac graphics processor to instantly drop old residue layers
        self.app.update_idletasks()

    def wrapped_load_local_tracks(self):
        """Runs the original track loader in main.py, then updates the scroller if it's open."""
        self.original_load_tracks()
        if self.scroll_frame is not None:
            self.refresh_scroll_list()

    def refresh_scroll_list(self):
        """Clears and rebuilds semi-transparent wide text row tracks."""
        if self.scroll_frame is None:
            return

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.app.track_list:
            no_songs_lbl = ctk.CTkLabel(
                self.scroll_frame, text="No Audio Entries Found Inside Local /tracks Directory", 
                font=("Arial", 12), text_color="#66666A"
            )
            no_songs_lbl.pack(pady=100)
            return

        for index, track_name in enumerate(self.app.track_list):
            clean_display_title = track_name.replace(".mp3", "")

            track_btn = ctk.CTkButton(
                self.scroll_frame, 
                text=f"  [{index + 1:02d}]    {clean_display_title}", 
                font=("Arial", 13), 
                anchor="w",
                height=45, 
                fg_color="transparent", 
                text_color="#CCCCCC",
                hover_color="#202028", 
                corner_radius=0,
                border_width=0,
                command=lambda idx=index: self.select_track_from_scroller(idx)
            )
            track_btn.pack(fill="x", pady=2, padx=10)

    def select_track_from_scroller(self, track_index):
        """Changes the track pointer index and commands the app engine to execute playback."""
        self.app.current_track_index = track_index
        self.app.play_current_track()