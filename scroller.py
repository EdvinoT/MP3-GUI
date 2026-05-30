import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import os

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Takes the main app instance so this separate module can hijack
        the ACCESS SONGS button and inject a true translucent canvas overlay.
        """
        self.app = main_app_instance
        self.is_open = False  # Track whether the list page is active
        self.scroll_frame = None

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
        """Alters the background image to add a translucent tint layer and reveals the tracks."""
        self.is_open = True
        
        # 1. Hide the main operational menu buttons so they don't peek through
        self.app.btn_access.place_forget()
        self.app.btn_playlist.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_off.place_forget()

        # 2. Apply a true alpha-channel translucent dark mask directly over the background image pixels
        if self.app.pil_bg_image:
            w = self.app.bg_canvas.winfo_width()
            h = self.app.bg_canvas.winfo_height()
            
            # Create an exact sized copy of the background image converted to alpha-layers (RGBA)
            translucent_img = self.app.pil_bg_image.resize((w, h), Image.Resampling.LANCZOS).convert("RGBA")
            
            # Draw a dark overlay layer directly onto the image with an alpha value of 210 (out of 255)
            # This makes the background dark enough to read text, but keeps the underlying image visible!
            overlay = Image.new('RGBA', translucent_img.size, (10, 10, 13, 210))
            final_tinted_image = Image.alpha_composite(translucent_img, overlay)
            
            # Render it onto the existing background canvas
            self.app.bg_photo = ImageTk.PhotoImage(final_tinted_image)
            self.app.bg_canvas.delete("all")
            self.app.bg_canvas.create_image(0, 0, image=self.app.bg_photo, anchor="nw")

        # 3. Create a clean, transparent navigation layout container for the return controller
        self.nav_frame = ctk.CTkFrame(self.app, height=60, fg_color="transparent")
        self.nav_frame.place(relx=0, rely=0, relwidth=1, anchor="nw")

        btn_back = ctk.CTkButton(
            self.nav_frame, text="◀  BACK TO MENU", font=("Futura", 12),
            width=140, height=35, corner_radius=0,
            fg_color="#000000", text_color="#DDDDDD", hover_color="#151515",
            command=self.close_full_page_scroller
        )
        btn_back.pack(side="left", padx=20, pady=12)

        # 4. Spawn the giant scrolling frame directly on the app window with a transparent background
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.app, 
            fg_color="transparent", 
            corner_radius=0, 
            border_width=0
        )
        self.scroll_frame.place(relx=0.05, rely=0.12, relwidth=0.9, relheight=0.7)

        # Re-populate rows
        self.refresh_scroll_list()

    def close_full_page_scroller(self):
        """Restores the original clean background image and brings back the main menu options."""
        self.is_open = False

        # Destroy the scroll list and nav components
        if self.scroll_frame is not None:
            self.scroll_frame.destroy()
            self.scroll_frame = None
        if hasattr(self, 'nav_frame'):
            self.nav_frame.destroy()

        # Command the main app hub to recalculate and redraw its default clean background layout
        self.app.setup_background_canvas()

        # Bring your home menu selection buttons back to their original screen positions
        self.app.btn_access.place(relx=0.5, rely=0.38, anchor="center")
        self.app.btn_playlist.place(relx=0.5, rely=0.48, anchor="center")
        self.app.btn_add.place(relx=0.5, rely=0.58, anchor="center")
        self.app.btn_off.place(relx=0.5, rely=0.68, anchor="center")

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

            # Rows use a very light outline or transparent fill so the tinted image shows right through
            track_btn = ctk.CTkButton(
                self.scroll_frame, 
                text=f"  [{index + 1:02d}]    {clean_display_title}", 
                font=("Arial", 13), 
                anchor="w",
                height=45, 
                fg_color="#18181F", # Very dark tinted block
                text_color="#CCCCCC",
                hover_color="#252530", # Highlights beautifully on hover
                corner_radius=0,
                border_width=0,
                command=lambda idx=index: self.select_track_from_scroller(idx)
            )
            track_btn.pack(fill="x", pady=4, padx=10)

    def select_track_from_scroller(self, track_index):
        """Changes the track pointer index and commands the app engine to execute playback."""
        self.app.current_track_index = track_index
        self.app.play_current_track()