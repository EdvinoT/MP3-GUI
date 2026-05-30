import customtkinter as ctk
import os

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Takes the main app instance so this separate module can hijack
        the ACCESS SONGS button and project a 100% true transparent vertical track lane.
        """
        self.app = main_app_instance
        self.archive_screen = None  
        self.scroll_offset = 0  # Tracks our custom scroll position

        # Overwrite the default button command in main.py to trigger our view creator
        self.app.btn_access.configure(command=self.open_full_page_scroller)

        # Intercept the track-loading system to update our scroller if it's currently open
        self.original_load_tracks = self.app.load_local_tracks
        self.app.load_local_tracks = self.wrapped_load_local_tracks

    def open_full_page_scroller(self):
        """Spawns a vertical lane stretching from the absolute top to the absolute bottom."""
        if self.archive_screen is not None:
            return  

        # 1. HIDE EVERYTHING: Main menu buttons AND the lower audio playback controls deck!
        self.app.btn_access.place_forget()
        self.app.btn_playlist.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_off.place_forget()
        self.app.playback_frame.place_forget()

        self.scroll_offset = 0

        # 2. TRUE TRANSPARENT CONTAINER: Using a standard frame allows true transparency over the canvas image
        self.archive_screen = ctk.CTkFrame(
            self.app, 
            fg_color="transparent", 
            corner_radius=0, 
            border_width=0
        )
        self.archive_screen.place(relx=0.2, rely=0.0, relwidth=0.6, relheight=1.0)

        # 3. HEADER ROW: Transparent bar at the top for your Back button control
        self.nav_frame = ctk.CTkFrame(self.archive_screen, height=60, fg_color="transparent")
        self.nav_frame.pack(fill="x", side="top", pady=(20, 5))

        btn_back = ctk.CTkButton(
            self.nav_frame, text="◀  BACK TO MENU", font=("Futura", 11),
            width=130, height=35, corner_radius=0,
            fg_color="#000000", text_color="#DDDDDD", hover_color="#151515",
            command=self.close_full_page_scroller
        )
        btn_back.pack(side="left", padx=15)

        # 4. TRACK CONTAINER PANEL: A completely open frame with a thin boundary wire
        self.track_container = ctk.CTkFrame(
            self.archive_screen,
            fg_color="transparent",
            corner_radius=0,
            border_width=1,
            border_color="#222226"
        )
        self.track_container.pack(fill="both", expand=True, padx=15, pady=(5, 20))

        # Bind the mouse wheel directly to the screen to handle custom scrolling mechanics
        self.app.bind("<MouseWheel>", self.on_mouse_scroll)
        # Linux compatibility
        self.app.bind("<Button-4>", self.on_mouse_scroll)
        self.app.bind("<Button-5>", self.on_mouse_scroll)

        # Render the tracks
        self.refresh_scroll_list()

    def on_mouse_scroll(self, event):
        """Custom pure-Python scroll wheel physics handler."""
        if not self.app.track_list:
            return

        # Handle Mac/Windows vs Linux scroll signals
        if event.num == 4 or event.delta > 0:
            self.scroll_offset = max(0, self.scroll_offset - 1)
        elif event.num == 5 or event.delta < 0:
            # Prevent scrolling down past the total number of tracks that fit on screen (approx 10 rows)
            max_scroll = max(0, len(self.app.track_list) - 10)
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)

        self.refresh_scroll_list()

    def close_full_page_scroller(self):
        """Destroys the archive screen layer completely and restores the main media center dashboard."""
        # Unbind the scrolling events so they don't break the main menu
        self.app.unbind("<MouseWheel>")
        self.app.unbind("<Button-4>")
        self.app.unbind("<Button-5>")

        if self.archive_screen is not None:
            self.archive_screen.destroy()
            self.archive_screen = None

        # 1. Bring back your home selection menu options
        self.app.btn_access.place(relx=0.5, rely=0.38, anchor="center")
        self.app.btn_playlist.place(relx=0.5, rely=0.48, anchor="center")
        self.app.btn_add.place(relx=0.5, rely=0.58, anchor="center")
        self.app.btn_off.place(relx=0.5, rely=0.68, anchor="center")

        # 2. Bring back the lower audio playback controls deck!
        self.app.playback_frame.place(relx=0.5, rely=0.85, anchor="center")

        # Force a hard display pipeline redraw
        self.app.update_idletasks()

    def wrapped_load_local_tracks(self):
        """Runs the original track loader in main.py, then updates the scroller if it's open."""
        self.original_load_tracks()
        if self.archive_screen is not None:
            self.refresh_scroll_list()

    def refresh_scroll_list(self):
        """Clears and rebuilds text row tracks based on current scroll math updates."""
        if self.archive_screen is None:
            return

        # Clear out old widget views inside the open frame
        for widget in self.track_container.winfo_children():
            widget.destroy()

        if not self.app.track_list:
            no_songs_lbl = ctk.CTkLabel(
                self.track_container, text="No Audio Entries Found Inside Local /tracks Directory", 
                font=("Arial", 12), text_color="#66666A"
            )
            no_songs_lbl.pack(pady=100)
            return

        # Calculate visible frame slice range based on mouse offset (shows up to 11 tracks at once)
        visible_tracks = self.app.track_list[self.scroll_offset : self.scroll_offset + 11]

        for index, track_name in enumerate(visible_tracks):
            actual_track_index = index + self.scroll_offset
            clean_display_title = track_name.replace(".mp3", "")

            # Set completely transparent button layouts! 
            # Only the text and hover states are rendered, keeping the background entirely pristine.
            track_btn = ctk.CTkButton(
                self.track_container, 
                text=f"  [{actual_track_index + 1:02d}]    {clean_display_title}", 
                font=("Arial", 12), 
                anchor="w",
                height=42, 
                fg_color="transparent", 
                text_color="#CCCCCC",
                hover_color="#14141A", # Faint reactive row highlight on hover
                corner_radius=0,
                border_width=0,
                command=lambda idx=actual_track_index: self.select_track_from_scroller(idx)
            )
            track_btn.pack(fill="x", pady=2, padx=5)

    def select_track_from_scroller(self, track_index):
        """Changes the track pointer index and commands the app engine to execute playback."""
        self.app.current_track_index = track_index
        self.app.play_current_track()