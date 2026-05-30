import customtkinter as ctk
import os

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Takes the main app instance so this separate module can inject 
        a scrollable track list onto the existing UI layout.
        """
        self.app = main_app_instance
        
        # Build the scrolling frame container on the left side
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.app, width=300, height=320, 
            fg_color="#08080A", label_text="ACCESS SONGS",
            label_font=("Futura", 12), label_text_color="#888888",
            corner_radius=0, border_width=1, border_color="#1A1A1F"
        )
        self.scroll_frame.place(relx=0.1, rely=0.32, anchor="nw")

        # Intercept the original track-loading system to automatically update our scroller
        self.original_load_tracks = self.app.load_local_tracks
        self.app.load_local_tracks = self.wrapped_load_local_tracks

        # Populate the list right away on startup
        self.refresh_scroll_list()

    def wrapped_load_local_tracks(self):
        """Runs the original track loader in main.py, then immediately refreshes the UI list."""
        self.original_load_tracks()
        self.refresh_scroll_list()

    def refresh_scroll_list(self):
        """Clears and rebuilds small, clickable track rows inside the scroller view."""
        # Clear out any old widgets in the frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.app.track_list:
            no_songs_lbl = ctk.CTkLabel(
                self.scroll_frame, text="Empty Directory Bank", 
                font=("Arial", 11), text_color="#555555"
            )
            no_songs_lbl.pack(pady=20)
            return

        # Populate with small interactive button items for every music file
        for index, track_name in enumerate(self.app.track_list):
            clean_display_title = track_name.replace(".mp3", "")
            
            # Shorten display strings if titles are too long for the sidebar layout
            if len(clean_display_title) > 32:
                clean_display_title = clean_display_title[:29] + "..."

            track_btn = ctk.CTkButton(
                self.scroll_frame, 
                text=f"{index + 1}. {clean_display_title}", 
                font=("Arial", 11), 
                anchor="w",
                height=28, 
                fg_color="transparent", 
                text_color="#AAAAAA",
                hover_color="#18181C", 
                corner_radius=0,
                command=lambda idx=index: self.select_track_from_scroller(idx)
            )
            track_btn.pack(fill="x", pady=2)

    def select_track_from_scroller(self, track_index):
        """Changes the track pointer index and commands the app engine to play it."""
        self.app.current_track_index = track_index
        self.app.play_current_track()