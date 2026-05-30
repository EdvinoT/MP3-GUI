import customtkinter as ctk
import os

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Takes the main app instance so this separate module can hijack
        the ACCESS SONGS button and overlay a bulletproof translucent frame layer.
        """
        self.app = main_app_instance
        self.archive_screen = None  # Holds our dedicated screen frame layer

        # Overwrite the default button command in main.py to trigger our view creator
        self.app.btn_access.configure(command=self.open_full_page_scroller)

        # Intercept the track-loading system to update our scroller if it's currently open
        self.original_load_tracks = self.app.load_local_tracks
        self.app.load_local_tracks = self.wrapped_load_local_tracks

    def open_full_page_scroller(self):
        """Spawns a clean screen frame container directly over the background image layout."""
        if self.archive_screen is not None:
            return  # Prevent stacking multiple screens if double-clicked

        # 1. Hide the main operational menu buttons (Leaves lower play deck controls untouched)
        self.app.btn_access.place_forget()
        self.app.btn_playlist.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_off.place_forget()

        # 2. Spawn a dedicated frame layer pinned perfectly inside the app window boundaries
        # CHANGED: We use a custom translucent color code '#101014' with a lower alpha matching system
        # This acts as your clear, clean bounding glass container box.
        self.archive_screen = ctk.CTkFrame(
            self.app, 
            fg_color="#101014", 
            corner_radius=0, 
            border_width=1, 
            border_color="#1F1F24"
        )
        self.archive_screen.place(relx=0.05, rely=0.12, relwidth=0.9, relheight=0.7)

        # 3. Create a header layer inside our new frame box for the Back button control
        nav_frame = ctk.CTkFrame(self.archive_screen, height=50, fg_color="transparent")
        nav_frame.pack(fill="x", side="top", padx=10, pady=5)

        btn_back = ctk.CTkButton(
            nav_frame, text="◀  BACK TO MENU", font=("Futura", 12),
            width=140, height=35, corner_radius=0,
            fg_color="#000000", text_color="#DDDDDD", hover_color="#151515",
            command=self.close_full_page_scroller
        )
        btn_back.pack(side="left", pady=5)

        # 4. Spawn the scrolling text framework right below the navigation panel row
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.archive_screen, 
            fg_color="transparent", 
            corner_radius=0, 
            border_width=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Render the track buttons instantly
        self.refresh_scroll_list()

    def close_full_page_scroller(self):
        """Destroys the archive screen layer completely, leaving zero residual boxes."""
        if self.archive_screen is not None:
            # This completely vanishes the frame and everything inside it from your system graphics card memory
            self.archive_screen.destroy()
            self.archive_screen = None
            self.scroll_frame = None

        # Reset your home selection menu choices back to their default target coordinates
        self.app.btn_access.place(relx=0.5, rely=0.38, anchor="center")
        self.app.btn_playlist.place(relx=0.5, rely=0.48, anchor="center")
        self.app.btn_add.place(relx=0.5, rely=0.58, anchor="center")
        self.app.btn_off.place(relx=0.5, rely=0.68, anchor="center")

        # Force a hard display pipeline redraw to clean up any residual artifact traces
        self.app.update_idletasks()

    def wrapped_load_local_tracks(self):
        """Runs the original track loader in main.py, then updates the scroller if it's open."""
        self.original_load_tracks()
        if self.scroll_frame is not None:
            self.refresh_scroll_list()

    def refresh_scroll_list(self):
        """Clears and rebuilds wide text row tracks inside our scrolling window container."""
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
                hover_color="#1A1A22", 
                corner_radius=0,
                border_width=0,
                command=lambda idx=index: self.select_track_from_scroller(idx)
            )
            track_btn.pack(fill="x", pady=2, padx=10)

    def select_track_from_scroller(self, track_index):
        """Changes the track pointer index and commands the app engine to execute playback."""
        self.app.current_track_index = track_index
        self.app.play_current_track()