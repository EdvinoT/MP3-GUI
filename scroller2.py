import customtkinter as ctk
from tkinter import messagebox, Canvas
import os

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Takes the main app instance to project a compact handheld track menu lane.
        Optimized specifically for a 480x320 screen resolution on a Pi Zero 2 W.
        """
        self.app = main_app_instance
        self.is_open = False  
        self.scroll_offset = 0
        self.visible_count = 6  # Fits perfectly in the 320px vertical space
        
        self.canvas_item_ids = []
        self.hover_strip_id = None    
        self.currently_hovered_idx = None  
        
        # Lock coordinates to handheld screen dimensions
        self.LANE_X1 = 30
        self.LANE_X2 = 450
        self.ROW_START_Y = 110
        self.LINE_HEIGHT = 30

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
        """Hides menu widgets and shifts the display canvas into a fast handheld scrolling matrix."""
        self.is_open = True
        self.scroll_offset = 0
        
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
        
        # 1. HIDE MAIN MENU INTERFACE
        self.app.btn_access.place_forget()
        self.app.btn_playlist.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_off.place_forget()
        self.app.playback_frame.place_forget()

        # 2. CLEAR PREVIOUS TITLE LOGOS (Redrawn tightly via text list)
        self.app.bg_canvas.delete("all")
        self.app.setup_background_canvas()

        # 3. Bind input controllers (Touch/Mouse)
        self.app.bind("<MouseWheel>", self.on_mouse_scroll)
        self.app.bind("<Button-4>", self.on_mouse_scroll)
        self.app.bind("<Button-5>", self.on_mouse_scroll)
        self.app.bg_canvas.bind("<Button-1>", self.on_canvas_click)
        self.app.bg_canvas.bind("<Motion>", self.on_canvas_hover)

        self.refresh_scroll_list()

    def on_mouse_scroll(self, event):
        """Handles page navigation calculations when the mouse wheel or touch-drag spins."""
        if not self.app.track_list:
            return

        old_offset = self.scroll_offset

        if event.num == 4 or event.delta > 0:
            self.scroll_offset = max(0, self.scroll_offset - 1)
        elif event.num == 5 or event.delta < 0:
            max_scroll = max(0, len(self.app.track_list) - self.visible_count)
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)

        if self.scroll_offset != old_offset and hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("scroll")

        self.refresh_scroll_list()

    def on_canvas_hover(self, event):
        """Detects if the cursor is hovering over a track row lane to trigger a flat highlight."""
        if not self.is_open:
            return

        current_item = self.app.bg_canvas.find_withtag("current")
        
        if current_item:
            item_id = current_item[0]
            tags = self.app.bg_canvas.gettags(item_id)
            
            if "back_btn" in tags:
                self.clear_hover_strip()
                self.app.bg_canvas.itemconfig(item_id, fill="#FF5555")
                return
            else:
                self.app.bg_canvas.itemconfig("back_btn", fill="#000000")

            if "track_item" in tags:
                for tag in tags:
                    if tag.startswith("track_") and tag != "track_item":
                        track_idx = int(tag.split("_")[1])
                        
                        if self.currently_hovered_idx != track_idx:
                            self.clear_hover_strip()
                            self.currently_hovered_idx = track_idx
                            
                            bbox = self.app.bg_canvas.bbox(item_id)
                            if bbox:
                                _, y1, _, y2 = bbox
                                padding = 4  
                                self.draw_flat_highlight(self.LANE_X1, y1 - padding, self.LANE_X2, y2 + padding)
                        return
        else:
            canvas_y = event.y
            
            estimated_row = (canvas_y - self.ROW_START_Y + (self.LINE_HEIGHT // 2)) // self.LINE_HEIGHT
            visible_count = min(self.visible_count, len(self.app.track_list) - self.scroll_offset)
            
            if 0 <= estimated_row < visible_count:
                track_idx = estimated_row + self.scroll_offset
                if self.currently_hovered_idx != track_idx:
                    self.clear_hover_strip()
                    for item_id in self.canvas_item_ids:
                        tags = self.app.bg_canvas.gettags(item_id)
                        if f"track_{track_idx}" in tags:
                            self.currently_hovered_idx = track_idx
                            bbox = self.app.bg_canvas.bbox(item_id)
                            if bbox:
                                _, y1, _, y2 = bbox
                                padding = 4
                                self.draw_flat_highlight(self.LANE_X1, y1 - padding, self.LANE_X2, y2 + padding)
                            return
            else:
                self.clear_hover_strip()

    def draw_flat_highlight(self, x1, y1, x2, y2):
        """Renders an instant solid focus background block behind the text row."""
        if not self.is_open:
            return
        # Using a dark-gray highlight theme block to remain friendly on high-contrast small screens
        self.hover_strip_id = self.app.bg_canvas.create_rectangle(
            x1, y1, x2, y2, fill="#252528", outline=""
        )
        self.app.bg_canvas.tag_lower(self.hover_strip_id)
        for item_id in self.canvas_item_ids:
            self.app.bg_canvas.tag_raise(item_id)

    def clear_hover_strip(self):
        """Safely removes the active tracking row background asset."""
        if self.hover_strip_id:
            self.app.bg_canvas.delete(self.hover_strip_id)
            self.hover_strip_id = None
        self.currently_hovered_idx = None

    def close_full_page_scroller(self):
        """Clears text elements, wipes structural bindings, and restores home core layout."""
        self.is_open = False

        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")

        self.app.unbind("<MouseWheel>")
        self.app.unbind("<Button-4>")
        self.app.unbind("<Button-5>")
        self.app.bg_canvas.unbind("<Button-1>")
        self.app.bg_canvas.unbind("<Motion>")

        self.clear_hover_strip()
        self.clear_canvas_items()
        
        self.app.bg_canvas.delete("all")
        self.app.setup_background_canvas()

        # Re-place default menus right where they belong on the small panel
        self.app.btn_access.place(x=60, y=140)
        self.app.btn_playlist.place(x=60, y=190)
        self.app.btn_add.place(x=260, y=140)
        self.app.btn_off.place(x=260, y=190)
        self.app.playback_frame.place(relx=0.5, rely=0.85, anchor="center")

        self.app.update_idletasks()

    def wrapped_load_local_tracks(self):
        """Runs original track loader system, refreshing text vectors dynamically if active."""
        self.original_load_tracks()
        if self.is_open:
            self.refresh_scroll_list()

    def clear_canvas_items(self):
        """Wipes custom track layout text assets cleanly from display architecture."""
        for item_id in self.canvas_item_ids:
            self.app.bg_canvas.delete(item_id)
        self.canvas_item_ids.clear()

    def refresh_scroll_list(self):
        """Draws track catalog text rows built tightly to accommodate handheld dimensions."""
        if not self.is_open:
            return

        self.clear_hover_strip()
        self.clear_canvas_items()

        # --- COMPACT UPPER MENU CONTROLS ---
        back_id = self.app.bg_canvas.create_text(
            45, 80, text="◀  MENU", 
            font=("Futura", 10, "bold"), fill="#000000", anchor="w", tags=("back_btn",)
        )
        self.canvas_item_ids.append(back_id)

        if not self.app.track_list:
            empty_id = self.app.bg_canvas.create_text(
                self.app.SCREEN_WIDTH // 2, 180, text="Empty Local Audio Catalog",
                font=("Arial", 11), fill="#55555A", anchor="center"
            )
            self.canvas_item_ids.append(empty_id)
            return

        # --- AUDIO CATALOG ROWS ENGINE ---
        visible_tracks = self.app.track_list[self.scroll_offset : self.scroll_offset + self.visible_count]

        for index, track_name in enumerate(visible_tracks):
            actual_track_index = index + self.scroll_offset
            clean_display_title = track_name.replace(".mp3", "")
            
            if len(clean_display_title) > 32:
                clean_display_title = clean_display_title[:29] + "..."
                
            y_pos = self.ROW_START_Y + (index * self.LINE_HEIGHT)
            display_string = f"[{actual_track_index + 1:02d}]  {clean_display_title}"

            # 1. DRAW COMPACT ROW TEXT (Changed fill color to #000000)
            track_id = self.app.bg_canvas.create_text(
                50, y_pos, text=display_string,
                font=("Arial", 11), fill="#000000", anchor="w"
            )
            self.canvas_item_ids.append(track_id)
            self.app.bg_canvas.itemconfig(track_id, tags=(f"track_{actual_track_index}", "track_item"))

            # 2. LOW OVERHEAD THIN ROW DIVIDER BOUNDS
            line_y = y_pos + 14  
            divider_id = self.app.bg_canvas.create_line(
                self.LANE_X1, line_y, self.LANE_X2, line_y,
                fill="#202025", width=1
            )
            self.canvas_item_ids.append(divider_id)

    def on_canvas_click(self, event):
        """Processes precise pointer clicks on floating text list links."""
        clicked_item = self.app.bg_canvas.find_withtag("current")
        if not clicked_item:
            return
            
        tags = self.app.bg_canvas.gettags(clicked_item[0])
        
        if "back_btn" in tags:
            self.close_full_page_scroller()
            return
            
        for tag in tags:
            if tag.startswith("track_") and tag != "track_item":
                if hasattr(self.app, 'play_ui_sound'):
                    self.app.play_ui_sound("click")
                    
                track_index = int(tag.split("_")[1])
                self.app.current_track_index = track_index
                self.app.play_current_track()
                break