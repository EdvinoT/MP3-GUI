import customtkinter as ctk
import os

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Takes the main app instance so this separate module can hijack
        the ACCESS SONGS button and project a translucent vertical track lane.
        """
        self.app = main_app_instance
        self.archive_screen = None  

        # Overwrite the default button command in main.py to trigger our view creator
        self.app.btn_access.configure(command=self.open_full_page_scroller)

        # Intercept the track-loading system to update our scroller if it's currently open
        self.original_load_tracks = self.app.load_local_tracks
        self.app.load_local_tracks = self.wrapped_load_local_tracks

    def open_full_page_scroller(self):
        """Spawns a vertical lane straight down the center over the background image layout."""
        if self.archive_screen is not None:
            return  

        # 1. Hide the main operational menu buttons (Leaves lower play deck controls untouched)
        self.app.btn_access.place_forget()
        self.app.btn_playlist.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_off.place_forget()

        # 2. FIXED: Changed fg_color to "transparent" so the frame itself doesn't block the background.
        # We place it from rely=0.0 (top) to relheight=0.82 (stops right above the music player deck).
        # We set relx=0.25 and relwidth=0.5 so it centers perfectly as a vertical channel.
        self.archive_screen = ctk.CTkFrame(
            self.app, 
            fg_color="transparent", 
            corner_radius=0, 
            border_width=0
        )
        self.archive_screen.place(relx=0.25, rely=0.0, relwidth=0.5, relheight=0.82)

        # 3. Create a header layer inside our new lane for the Back button control
        nav_frame = ctk.CTkFrame(self.archive_screen, height=50, fg_color="transparent")
        nav_frame.pack(fill="x", side="top", pady=(15, 5))

        btn_back = ctk.CTkButton(
            nav_frame, text="◀  BACK TO MENU", font=("Futura", 11),
            width=120, height=30, corner_radius=4,
            fg_color="#000000", text_color="#DDDDDD", hover_color="#151515",
            command=self.close_full_page_scroller
        )
        btn_back.pack(side="left", padx=10)

        # 4. Spawn the scrolling text framework right below the navigation panel row
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.archive_screen, 
            fg_color="transparent", 
            corner_radius=0, 
            border_width=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Render the track buttons instantly
        self.refresh_scroll_list()

    def close_full_page_scroller(self):
        """Destroys the archive screen layer completely, leaving zero residual boxes."""
        if self.archive_screen is not None:
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
        """Clears and rebuilds text row tracks inside our scrolling window container."""
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

            # FIXED: We use a very low opacity dark color ("#121217") for the buttons.
            # Because the buttons are stacked closely, they build a beautiful translucent column 
            # where you can still see the artwork on the far left and far right of the app!
            track_btn = ctk.CTkButton(
                self.scroll_frame, 
                text=f"  [{index + 1:02d}]    {clean_display_title}", 
                font=("Arial", 12), 
                anchor="w",
                height=40, 
                fg_color="#121217", 
                text_color="#CCCCCC",
                hover_color="#22222A", 
                corner_radius=4,
                border_width=0,
                command=lambda idx=index: self.select_track_from_scroller(idx)
            )
            track_btn.pack(fill="x", pady=2, padx=10)

    def select_track_from_scroller(self, track_index):
        """Changes the track pointer index and commands the app engine to execute playback."""
        self.app.current_track_index = track_index
        self.app.play_current_track()