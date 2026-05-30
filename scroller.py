import customtkinter as ctk
import os

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Takes the main app instance so this separate module can hijack
        the ACCESS SONGS button and overlay a full-page scroll menu.
        """
        self.app = main_app_instance
        self.page_overlay = None  # Holds our full-screen container frame

        # Overwrite the default button command in main.py to trigger our custom page load
        self.app.btn_access.configure(command=self.open_full_page_scroller)

        # Intercept the track-loading system to update our scroller if it's currently open
        self.original_load_tracks = self.app.load_local_tracks
        self.app.load_local_tracks = self.wrapped_load_local_tracks

    def open_full_page_scroller(self):
        """Spawns a full-window layout over the background image."""
        if self.page_overlay is not None:
            return  # Safety guard to prevent double-stacking frames

        # Create a massive master container frame pinned across the entire window view
        self.page_overlay = ctk.CTkFrame(self.app, fg_color="#0D0D10")
        self.page_overlay.place(x=0, y=0, relwidth=1, relheight=1)

        # --- NAVIGATION HEADER BAR ---
        nav_bar = ctk.CTkFrame(self.page_overlay, height=60, fg_color="#08080A", corner_radius=0)
        nav_bar.pack(fill="x", side="top")

        # Minimalist Return Button positioned inside our navigation bar layout
        btn_back = ctk.CTkButton(
            nav_bar, text="◀  BACK TO MENU", font=("Futura", 12),
            width=140, height=35, corner_radius=0,
            fg_color="#000000", text_color="#DDDDDD", hover_color="#151515",
            command=self.close_full_page_scroller
        )
        btn_back.pack(side="left", padx=20, pady=12)

        # Small indicator text showing current catalog status profiles
        page_title = ctk.CTkLabel(
            nav_bar, text="LOCAL AUDIO ARCHIVE STORAGE", 
            font=("Futura", 11), text_color="#666666"
        )
        page_title.pack(side="right", padx=25)

        # --- THE GIANT SEAMLESS SCROLLER ---
        # Takes up all remaining vertical screen real estate down the interface plane
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.page_overlay, 
            fg_color="transparent", 
            corner_radius=0, 
            border_width=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Instantly compile rows
        self.refresh_scroll_list()

    def close_full_page_scroller(self):
        """Destroys the top frame page cleanly to expose core dashboard menu options again."""
        if self.page_overlay is not None:
            self.page_overlay.destroy()
            self.page_overlay = None
            self.scroll_frame = None

    def wrapped_load_local_tracks(self):
        """Runs the original track loader in main.py, then updates the scroller if it's currently open."""
        self.original_load_tracks()
        if self.scroll_frame is not None:
            self.refresh_scroll_list()

    def refresh_scroll_list(self):
        """Clears and rebuilds wide, clickable track rows inside the giant scroller view."""
        if self.scroll_frame is None:
            return

        # Clear out any old widgets in the frame container
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.app.track_list:
            no_songs_lbl = ctk.CTkLabel(
                self.scroll_frame, text="No Audio Entries Found Inside Local /tracks Directory", 
                font=("Arial", 12), text_color="#555555"
            )
            no_songs_lbl.pack(pady=100)
            return

        # Populate wide button blocks for every music track entry detected
        for index, track_name in enumerate(self.app.track_list):
            clean_display_title = track_name.replace(".mp3", "")

            # Beautiful wide row button design matching your interface framework aesthetic
            track_btn = ctk.CTkButton(
                self.scroll_frame, 
                text=f"  [{index + 1:02d}]    {clean_display_title}", 
                font=("Arial", 13), 
                anchor="w",
                height=45, 
                fg_color="#121216", 
                text_color="#CCCCCC",
                hover_color="#1C1C22", 
                corner_radius=0,
                command=lambda idx=index: self.select_track_from_scroller(idx)
            )
            track_btn.pack(fill="x", pady=3, padx=10)

    def select_track_from_scroller(self, track_index):
        """Changes the track pointer index and commands the app engine to execute playback."""
        self.app.current_track_index = track_index
        self.app.play_current_track()