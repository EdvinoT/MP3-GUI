import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import os

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Takes the main app instance to project a widened frosted glass lane.
        Features liquid-smooth alpha row fade animations and clean track dividers.
        """
        self.app = main_app_instance
        self.is_open = False  
        self.scroll_offset = 0
        self.visible_count = 13  
        
        self.canvas_item_ids = []
        self.hover_strip_id = None    
        self.currently_hovered_idx = None  
        
        # ANIMATION STATE TRACKING
        self.animation_job = None      
        self.current_alpha = 0         # Starting opacity (0 = completely invisible)
        self.target_alpha = 40         # Maximum target highlight opacity (out of 255)
        self.active_row_coords = None  # Caches bounds of the row currently fading in

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
        
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
        
        # 1. HIDE EVERYTHING: Clear out main menu buttons and audio deck entirely
        self.app.btn_access.place_forget()
        self.app.btn_playlist.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_off.place_forget()
        self.app.playback_frame.place_forget()

        # 2. GENERATE LIGHT FROSTED GLASS TINT
        if self.app.pil_bg_image:
            w = self.app.bg_canvas.winfo_width()
            h = self.app.bg_canvas.winfo_height()
            if w <= 1: w, h = 800, 600
            
            base_img = self.app.pil_bg_image.resize((w, h), Image.Resampling.LANCZOS).convert("RGBA")
            overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            draw.rectangle(
                [int(w * 0.10), 0, int(w * 0.90), h], 
                fill=(235, 235, 240, 95),
                outline=(255, 255, 255, 40),
                width=1
            )
            
            final_tinted_image = Image.alpha_composite(base_img, overlay)
            self.app.bg_photo = ImageTk.PhotoImage(final_tinted_image)
            self.app.bg_canvas.delete("all")
            self.app.bg_canvas.create_image(0, 0, image=self.app.bg_photo, anchor="nw")

        # 3. Bind input controllers
        self.app.bind("<MouseWheel>", self.on_mouse_scroll)
        self.app.bind("<Button-4>", self.on_mouse_scroll)
        self.app.bind("<Button-5>", self.on_mouse_scroll)
        self.app.bg_canvas.bind("<Button-1>", self.on_canvas_click)
        self.app.bg_canvas.bind("<Motion>", self.on_canvas_hover)

        self.refresh_scroll_list()

    def on_mouse_scroll(self, event):
        """Handles page navigation calculations when the mouse wheel spins."""
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
        """Detects if the cursor is hovering over a track to trigger smooth alpha fading loops."""
        if not self.is_open:
            return

        current_item = self.app.bg_canvas.find_withtag("current")
        w = self.app.bg_canvas.winfo_width()
        if w <= 1: w = 800
        
        if current_item:
            item_id = current_item[0]
            tags = self.app.bg_canvas.gettags(item_id)
            
            # Handle Back Button Hover
            if "back_btn" in tags:
                self.clear_hover_strip()
                self.app.bg_canvas.itemconfig(item_id, fill="#FF5555")
                return
            else:
                self.app.bg_canvas.itemconfig("back_btn", fill="#222226")

            # Handle Song Row Hover
            if "track_item" in tags:
                for tag in tags:
                    if tag.startswith("track_") and tag != "track_item":
                        track_idx = int(tag.split("_")[1])
                        
                        if self.currently_hovered_idx != track_idx:
                            self.currently_hovered_idx = track_idx
                            
                            if hasattr(self.app, 'play_ui_sound'):
                                self.app.play_ui_sound("scroll")
                            
                            self.clear_hover_strip()
                            
                            bbox = self.app.bg_canvas.bbox(item_id)
                            if bbox:
                                _, y1, _, y2 = bbox
                                padding = 8  # Expanded to look like full, substantial structural rows
                                
                                # Store the absolute row bounding dimensions for our background layer builder
                                self.active_row_coords = (int(w * 0.10) + 1, y1 - padding, int(w * 0.90) - 1, y2 + padding)
                                
                                # Reset true alpha values and trigger the linear interpolation renderer
                                self.current_alpha = 0
                                self.run_smooth_fade(item_id)
                        return

        # If the cursor escapes out to blank canvas space, clear everything back out
        self.clear_hover_strip()
        self.app.bg_canvas.itemconfig("back_btn", fill="#222226")

    def run_smooth_fade(self, text_item_id):
        """Gradually increments the layer's raw alpha channel value for a seamless glass fade."""
        if not self.is_open or self.active_row_coords is None:
            return
            
        if self.current_alpha < self.target_alpha:
            # Step speed size: increments by 4 alpha levels every 8ms for 60FPS fluid look
            self.current_alpha = min(self.target_alpha, self.current_alpha + 4)
            
            # Generate a temporary image clip matching the canvas size to render true alpha translucency
            w = self.app.bg_canvas.winfo_width()
            h = self.app.bg_canvas.winfo_height()
            if w <= 1: w, h = 800, 600
            
            # Create a completely transparent scratch canvas layer
            fade_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(fade_layer)
            
            # Draw a full pure white rectangle bar with the progressive alpha channel transparency value
            x1, y1, x2, y2 = self.active_row_coords
            draw.rectangle([x1, y1, x2, y2], fill=(255, 255, 255, self.current_alpha), outline="")
            
            # Convert to TK format and update the unique background item on the canvas
            self.hover_strip_photo = ImageTk.PhotoImage(fade_layer)
            
            if self.hover_strip_id:
                self.app.bg_canvas.itemconfig(self.hover_strip_id, image=self.hover_strip_photo)
            else:
                self.hover_strip_id = self.app.bg_canvas.create_image(0, 0, image=self.hover_strip_photo, anchor="nw")
                
            # Keep the background graphics underneath the song title text
            self.app.bg_canvas.tag_lower(self.hover_strip_id, text_item_id)
            
            # Loop next frame refresh step
            self.animation_job = self.app.after(8, lambda: self.run_smooth_fade(text_item_id))

    def clear_hover_strip(self):
        """Halts the alpha clock loop engine and deletes the custom background highlight image layer."""
        if self.animation_job:
            self.app.after_cancel(self.animation_job)
            self.animation_job = None
            
        if self.hover_strip_id:
            self.app.bg_canvas.delete(self.hover_strip_id)
            self.hover_strip_id = None
            
        self.currently_hovered_idx = None
        self.active_row_coords = None
        self.hover_strip_photo = None

    def close_full_page_scroller(self):
        """Clears text elements, wipes the light tint layer out, and returns to home core layout."""
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
        """Draws clean track text rows separated by thin, clean, low-opacity divider lines."""
        if not self.is_open:
            return

        self.clear_hover_strip()
        self.clear_canvas_items()
        
        w = self.app.bg_canvas.winfo_width()
        if w <= 1: w = 800

        # --- BACK LINK ---
        back_id = self.app.bg_canvas.create_text(
            int(w * 0.13), 35, text="◀  BACK TO MENU", 
            font=("Futura", 10, "bold"), fill="#222226", anchor="w", tags=("back_btn",)
        )
        self.canvas_item_ids.append(back_id)

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
        line_height = 36 

        for index, track_name in enumerate(visible_tracks):
            actual_track_index = index + self.scroll_offset
            clean_display_title = track_name.replace(".mp3", "")
            
            y_pos = start_y + (index * line_height)
            display_string = f"  [{actual_track_index + 1:02d}]    {clean_display_title}"

            # 1. DRAW TEXT ITEM
            track_id = self.app.bg_canvas.create_text(
                int(w * 0.13), y_pos, text=display_string,
                font=("Arial", 10), fill="#222226", anchor="w"
            )
            self.canvas_item_ids.append(track_id)
            self.app.bg_canvas.itemconfig(track_id, tags=(f"track_{actual_track_index}", "track_item"))

            # 2. FIXED: ADDED A VERY THIN SEPARATOR LINE BETWEEN EACH TRACK ROW
            # Draws a clean white line with low visibility across the bottom border edge of the text row lane
            line_y = y_pos + 17  
            divider_id = self.app.bg_canvas.create_line(
                int(w * 0.10), line_y, int(w * 0.90), line_y,
                fill="#FFFFFF", width=1
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