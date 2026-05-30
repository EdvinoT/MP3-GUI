import customtkinter as ctk
import os

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Takes the main app instance so this separate module can hijack
        the ACCESS SONGS button and draw text directly onto the main canvas.
        """
        self.app = main_app_instance
        self.is_open = False  
        self.scroll_offset = 0
        self.visible_count = 10  # Maximum number of tracks to display at once
        
        # Track canvas item IDs so we can cleanly wipe them out later
        self.canvas_item_ids = []

        # Overwrite the default button command in main.py to trigger our canvas view
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
        """Hides the menu widgets and draws text elements directly onto the wallpaper canvas."""
        self.is_open = True
        self.scroll_offset = 0
        
        # 1. HIDE EVERYTHING: Main menu buttons AND the lower audio playback controls deck
        self.app.btn_access.place_forget()
        self.app.btn_playlist.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_off.place_forget()
        self.app.playback_frame.place_forget()

        # 2. Bind the mouse wheel directly to the canvas to handle scrolling actions
        self.app.bind("<MouseWheel>", self.on_mouse_scroll)
        self.app.bind("<Button-4>", self.on_mouse_scroll)
        self.app.bind("<Button-5>", self.on_mouse_scroll)

        # 3. Bind click events to the canvas so we can click our text-buttons
        self.app.bg_canvas.bind("<Button-1>", self.on_canvas_click)

        # Render the text items
        self.refresh_scroll_list()

    def on_mouse_scroll(self, event):
        """Handles page navigation calculations when the mouse wheel spins."""
        if not self.app.track_list:
            return

        if event.num == 4 or event.delta > 0:
            self.scroll_offset = max(0, self.scroll_offset - 1)
        elif event.num == 5 or event.delta < 0:
            max_scroll = max(0, len(self.app.track_list) - self.visible_count)
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)

        self.refresh_scroll_list()

    def close_full_page_scroller(self):
        """Clears all text elements from the canvas and brings back the original dashboard interface."""
        self.is_open = False

        # Unbind all canvas events
        self.app.unbind("<MouseWheel>")
        self.app.unbind("<Button-4>")
        self.app.unbind("<Button-5>")
        self.app.bg_canvas.unbind("<Button-1>")

        # Wipe out all song list graphics from the canvas pipeline
        self.clear_canvas_items()

        # Redraw the original main menu titles ("IDLE SYSTEM", etc.)
        self.app.setup_background_canvas()

        # Bring back the core interactive dashboard menus
        self.app.btn_access.place(relx=0.5, rely=0.38, anchor="center")
        self.app.btn_playlist.place(relx=0.5, rely=0.48, anchor="center")
        self.app.btn_add.place(relx=0.5, rely=0.58, anchor="center")
        self.app.btn_off.place(relx=0.5, rely=0.68, anchor="center")
        self.app.playback_frame.place(relx=0.5, rely=0.85, anchor="center")

        self.app.update_idletasks()

    def wrapped_load_local_tracks(self):
        """Runs the original track loader in main.py,