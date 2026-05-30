import customtkinter as ctk
import os

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Takes the main app instance so this separate module can hijack
        the ACCESS SONGS button and project a full-height transparent vertical track lane.
        """
        self.app = main_app_instance
        self.archive_screen = None  

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

        # 2. FULL-HEIGHT CONTAINER: Spans from rely=0.0 (top) to relheight=1.0 (bottom)
        # Set to transparent so it does not mask your background picture at all.
        self.archive_screen = ctk.CTkFrame(
            self.app, 
            fg_color="transparent", 
            corner_radius=0, 
            border_width=0
        )
        self.archive_screen.place(relx=0.2, rely=0.0, relwidth=0.6, relheight=1.0)

        # 3. HEADER ROW: Transparent bar at the top for your Back button control
        nav_frame = ctk.CTkFrame(self.archive_screen, height=60, fg_color="transparent")
        nav_frame.pack(fill="x", side="top", pady=(20, 5))

        btn_back = ctk.CTkButton(
            nav_frame, text="◀  BACK TO MENU", font=("Futura", 11),
            width=130, height=35, corner_radius=0,
            fg_color="#000000", text_color="#DDDDDD", hover_color="#151515",
            command=self.close_full_page_scroller
        )
        btn_back.pack(side="left", padx=15)

        # 4. TRANSLUCENT SCROLLING WINDOW: Completely see-through background
        # We add a very subtle border outline to frame the vertical track lane elegantly
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.archive_screen, 
            fg_color="transparent", 
            corner_radius=0, 
            border_width=1,
            border_color="#222226"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=(5, 20))

        # Render the tracks
        self.refresh_scroll_list()

    def close_full_page_scroller(self):
        """Destroys the archive screen layer completely and restores the main media center dashboard."""
        if self.archive_screen is not None:
            self.archive_screen.destroy()
            self.archive_screen = None
            self.scroll_frame = None

        # 1. Bring back your home selection menu options
        self.app.btn_access.place(relx=0.5, rely=0.38, anchor="center")
        self.app.btn_playlist.place(relx=0.5, rely=0.48, anchor="center")
        self.app.btn_add.place(relx=0.5, rely=0.58, anchor="center")
        self.app.btn_off.place(relx=0.5, rely=0.68, anchor="center")

        # 2. Bring back the lower audio playback controls deck!
        self.app.playback_frame.place(relx=0.5, rely=0.85, anchor="center")

        # Force a hard display pipeline redraw to clear any graphical artifacts
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

            # Buttons use an ultra-faint dark gray background tint to create the "glass" look
            # while keeping your full background wallpaper completely visible underneath.
            track_btn = ctk.CTkButton(
                self.scroll_frame, 
                text=f"  [{index + 1:02d}]    {clean_display_title}", 
                font=("Arial", 12), 
                anchor="w",
                height=45, 
                fg_color="#0A0A0F", 
                text_color="#CCCCCC",
                hover_color="#181822", 
                corner_radius=0,
                border_width=0,
                command=lambda idx=index: self.select_track_from_scroller(idx)
            )
            track_btn.pack(fill="x", pady=2, padx=5)

    def select_track_from_scroller(self, track_index):
        """Changes the track pointer index and commands the app engine to execute playback."""
        self.app.current_track_index = track_index
        self.app.play_current_track()