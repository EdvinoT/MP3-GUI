import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import os

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Takes the main app instance so this separate module can hijack
        the ACCESS SONGS button and project a widened, frosted light-glass lane.
        """
        self.app = main_app_instance
        self.is_open = False  
        self.scroll_offset = 0
        self.visible_count = 13  # Increased count since font size is smaller now!
        
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
        """Hides menu widgets, generates a wide light-tint frosted glass overlay, and draws text."""
        self.is_open = True
        self.scroll_offset = 0
        
        # 1. HIDE EVERYTHING: Clear out main menu buttons and audio deck entirely
        self.app.btn_access.place_forget()
        self.app.btn_playlist.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_off.place_forget()
        self.app.playback_frame.place_forget()

        # 2. GENERATE LIGHT FROSTED GLASS TINT: Draw a semi-transparent light grey panel over the canvas
        if self.app.pil_bg_image:
            w = self.app.bg_canvas.winfo_width()
            h = self.app.bg_canvas.winfo_height()
            if w <= 1: w, h = 800, 600
            
            base_img = self.app.pil_bg_image.resize((w, h), Image.Resampling.LANCZOS).convert("RGBA")
            overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # FIXED: Widened the panel layout (now covers 10% width to 90% width)
            # FIXED: Changed tint to a bright light grey (235, 235, 240) with a highly transparent glass alpha (95)
            draw.rectangle(
                [int(w * 0.10), 0, int(w * 0.90), h], 
                fill=(235, 235, 240, 95),
                outline=(255, 255, 255, 40),
                width=1
            )
            
            # Layer the bright frost directly over your white wallpaper asset
            final_tinted_image = Image.alpha_composite(base_img, overlay)
            self.app.bg_photo = ImageTk.PhotoImage(final_tinted_image)
            self.app.bg_canvas.delete("all")
            self.app.bg_canvas.create_image(0, 0, image=self.app.bg_photo, anchor="nw")

        # 3. Bind input controllers
        self.app.bind("<MouseWheel>", self.on_mouse_scroll)
        self.app.bind("<Button-4>", self.on_mouse_scroll)
        self.app.bind("<Button-5>", self.on_mouse_scroll)
        self.app.bg_canvas.bind("<Button-1>", self.on_canvas_click)

        # Render rows
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
        """Clears text elements, wipes the light tint layer out, and returns to home core layout."""
        self.is_open = False

        self.app.unbind("<MouseWheel>")
        self.app.unbind("<Button-4>")
        self.app.unbind("<Button-5>")
        self.app.bg_canvas.unbind("<Button-1>")

        self.clear_canvas_items()
        self.app.setup_background_canvas()

        # Re-place default menus
        self.app.btn_access.place(relx=0.5, rely=0.38, anchor="center")
        self.app.btn_playlist.place(relx=0.5, rely=0.48, anchor="center")
        self.app.btn_add.place(relx=0.5, rely=0.58, anchor="center")
        self.app.btn_off.place(relx=0.5, rely=0.68, anchor="center")
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
        """Draws clean, compact dark slate track text strings directly onto the frosted glass layer."""
        if not self.is_open:
            return

        self.clear_canvas_items()
        
        w = self.app.bg_canvas.winfo_width()
        if w <= 1: w = 800

        # --- BACK LINK COORDINATES (Shifted left to line up with new wide margins) ---
        back_id = self.app.bg_canvas.create_text(
            int(w * 0.13), 35, text="◀  BACK TO MENU", 
            font=("Futura", 10, "bold"), fill="#222226", anchor="w"
        )
        self.canvas_item_ids.append(back_id)
        self.app.bg_canvas.itemconfig(back_id, tags=("back_btn",))

        if not self.app.track_list:
            empty_id = self.app.bg_canvas.create_text(
                w // 2, 250, text="Empty Local Audio Catalog",
                font=("Arial", 11), fill="#55555A", anchor="center"
            )
            self.canvas_item_ids.append(empty_id)
            return

        # --- COMPACT TEXT RENDER SYSTEM ---
        visible_tracks = self.app.track_list[self.scroll_offset : self.scroll_offset + self.visible_count]
        
        start_y = 85  
        line_height = 36 # Tighter row padding to allow more compact track lines on screen

        for index, track_name in enumerate(visible_tracks):
            actual_track_index = index + self.scroll_offset
            clean_display_title = track_name.replace(".mp3", "")
            
            y_pos = start_y + (index * line_height)
            display_string = f"  [{actual_track_index + 1:02d}]    {clean_display_title}"

            # FIXED: Smaller clean text sizing (font size 10)
            # FIXED: Dark Charcoal Slate color code ("#222226") to remain completely legible over light glass frost
            track_id = self.app.bg_canvas.create_text(
                int(w * 0.13), y_pos, text=display_string,
                font=("Arial", 10), fill="#222226", anchor="w"
            )
            self.canvas_item_ids.append(track_id)
            self.app.bg_canvas.itemconfig(track_id, tags=(f"track_{actual_track_index}", "track_item"))

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
                track_index = int(tag.split("_")[1])
                self.app.current_track_index = track_index
                self.app.play_current_track()
                break