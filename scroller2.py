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
        self.visible_count = 7  
        
        self.canvas_item_ids = []
        self.hover_strip_id = None    
        self.currently_hovered_idx = None  
        
        # FIX: Shifted columns hard-left to clear room on the right side of the screen
        self.LANE_X1 = 15
        self.LANE_X2 = 410
        self.ROW_START_Y = 110
        self.LINE_HEIGHT = 26

        self.app.btn_access.configure(command=self.toggle_full_page_scroller)

        self.original_load_tracks = self.app.load_local_tracks
        self.app.load_local_tracks = self.wrapped_load_local_tracks

    def toggle_full_page_scroller(self):
        if not self.is_open:
            self.open_full_page_scroller()
        else:
            self.close_full_page_scroller()

    def open_full_page_scroller(self):
        self.is_open = True
        self.scroll_offset = 0
        
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
        
        # Hide main operational selections
        self.app.btn_access.place_forget()
        if hasattr(self.app, 'btn_shuffle'):
            self.app.btn_shuffle.place_forget()
            
        self.app.btn_add.place_forget()
        self.app.btn_playlist.place_forget()
        
        # FIX: Keep settings icon visible but hide the shutdown trigger to block accidental power cutouts
        self.app.btn_off.place_forget()
        self.app.btn_quick_settings.place(x=15, y=266)
        
        self.app.playback_frame.place_forget()
        self.app.progress_container.place_forget()
        self.app.controls_dock.place_forget()
        if self.app.timer_text_id:
            self.app.bg_canvas.itemconfig(self.app.timer_text_id, state="hidden")

        self.clear_canvas_items()

        self.app.bind("<MouseWheel>", self.on_mouse_scroll)
        self.app.bind("<Button-4>", self.on_mouse_scroll)  
        self.app.bind("<Button-5>", self.on_mouse_scroll)  
        self.app.bind("<Up>", lambda e: self.force_scroll_direction(-1))
        self.app.bind("<Down>", lambda e: self.force_scroll_direction(1))
        
        self.app.bg_canvas.bind("<Button-1>", self.on_canvas_click)
        self.app.bg_canvas.bind("<Motion>", self.on_canvas_hover)

        if self.app.is_playing and self.app.track_list:
            current_track = self.app.track_list[self.app.current_track_index].replace(".mp3", "")
            self.app.update_status_text(f"▶ {current_track}", color="#FFB300")
        else:
            self.app.update_status_text("▪ SELECT TRACK MODULE ▪", color="#000000")

        self.refresh_scroll_list()

        if hasattr(self.app, 'battery_monitor'):
            self.app.battery_monitor._execute_telemetry_render()

    def force_scroll_direction(self, direction):
        if not self.app.track_list: return
        old_offset = self.scroll_offset
        
        if direction == -1:
            self.scroll_offset = max(0, self.scroll_offset - 1)
        elif direction == 1:
            max_scroll = max(0, len(self.app.track_list) - self.visible_count)
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
            
        if self.scroll_offset != old_offset:
            if hasattr(self.app, 'play_ui_sound'):
                self.app.play_ui_sound("scroll")
            self.refresh_scroll_list()

    def on_mouse_scroll(self, event):
        if not self.app.track_list: return
        
        if event.num == 4 or (event.delta and event.delta > 0):
            self.force_scroll_direction(-1)
        elif event.num == 5 or (event.delta and event.delta < 0):
            self.force_scroll_direction(1)

    def on_canvas_hover(self, event):
        if not self.is_open: return
        current_item = self.app.bg_canvas.find_withtag("current")
        
        if current_item:
            item_id = current_item[0]
            tags = self.app.bg_canvas.gettags(item_id)
            
            if "back_btn" in tags:
                self.clear_hover_strip()
                self.app.bg_canvas.itemconfig(item_id, fill="#FF5555")
                return
            elif "ui_scroll_up" in tags or "ui_scroll_down" in tags:
                self.clear_hover_strip()
                self.app.bg_canvas.itemconfig(item_id, fill="#00A8FF")
                return
            else:
                self.app.bg_canvas.itemconfig("back_btn", fill="#000000")
                self.app.bg_canvas.itemconfig("ui_scroll_up", fill="#555555")
                self.app.bg_canvas.itemconfig("ui_scroll_down", fill="#555555")

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
                                padding = 2  
                                self.animate_snap_highlight(self.LANE_X1, y1 - padding, self.LANE_X2, y2 + padding)
                        return
        else:
            self.clear_hover_strip()

    def animate_snap_highlight(self, x1, y1, x2, y2):
        if not self.is_open: return
        self.hover_strip_id = self.app.bg_canvas.create_rectangle(x1, y1, x2, y2, fill="#3A3A3F", outline="")
        self.app.bg_canvas.tag_lower(self.hover_strip_id)
        for item_id in self.canvas_item_ids:
            self.app.bg_canvas.tag_raise(item_id)
        self.app.after(40, lambda: self.settle_highlight_color())

    def settle_highlight_color(self):
        if self.hover_strip_id and self.is_open:
            self.app.bg_canvas.itemconfig(self.hover_strip_id, fill="#D1D1D6")

    def clear_hover_strip(self):
        if self.hover_strip_id:
            self.app.bg_canvas.delete(self.hover_strip_id)
            self.hover_strip_id = None
        self.currently_hovered_idx = None

    def close_full_page_scroller(self):
        self.is_open = False
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")

        self.app.unbind("<MouseWheel>")
        self.app.unbind("<Button-4>")
        self.app.unbind("<Button-5>")
        self.app.unbind("<Up>")
        self.app.unbind("<Down>")
        self.app.bg_canvas.unbind("<Button-1>")
        self.app.bg_canvas.unbind("<Motion>")

        self.clear_hover_strip()
        self.clear_canvas_items()

        # FIX: Exact positional alignment restoration based on main2.py geometry layout
        self.app.btn_access.place(x=60, y=140)
        if hasattr(self.app, 'btn_shuffle'):
            self.app.btn_shuffle.place(x=60, y=190)
            
        self.app.btn_add.place(x=260, y=140)
        self.app.btn_playlist.place(x=260, y=190)
        
        self.app.btn_quick_settings.place(x=15, y=266)
        self.app.btn_off.place(x=430, y=266)
        
        self.app.progress_container.place(relx=0.5, y=252, anchor="center")
        self.app.controls_dock.place(relx=0.5, y=284, anchor="center")
        if self.app.timer_text_id:
            self.app.bg_canvas.itemconfig(self.app.timer_text_id, state="normal")

        if self.app.is_playing and self.app.track_list:
            current_track = self.app.track_list[self.app.current_track_index].replace(".mp3", "")
            self.app.update_status_text(f"▶ {current_track}", color="#FFB300")
        else:
            self.app.update_status_text("▪ ONLINE ▪", color="#888888")

        if hasattr(self.app, 'battery_monitor'):
            self.app.battery_monitor._execute_telemetry_render()

        self.app.update_idletasks()

    def wrapped_load_local_tracks(self):
        self.original_load_tracks()
        if self.is_open: self.refresh_scroll_list()

    def clear_canvas_items(self):
        for item_id in self.canvas_item_ids:
            self.app.bg_canvas.delete(item_id)
        self.canvas_item_ids.clear()

    def refresh_scroll_list(self):
        if not self.is_open: return
        self.clear_hover_strip()
        self.clear_canvas_items()

        # FIX: Changed fonts to Courier New to match skinny aesthetic profiles
        back_id = self.app.bg_canvas.create_text(
            25, 80, text="◀  MENU", 
            font=("Courier New", 11, "bold"), fill="#DD2222", anchor="w", tags=("back_btn",)
        )
        self.canvas_item_ids.append(back_id)

        scr_up_id = self.app.bg_canvas.create_text(
            345, 80, text="▲",
            font=("Courier New", 12, "bold"), fill="#555555", anchor="center", tags=("ui_scroll_up",)
        )
        scr_down_id = self.app.bg_canvas.create_text(
            385, 80, text="▼",
            font=("Courier New", 12, "bold"), fill="#555555", anchor="center", tags=("ui_scroll_down",)
        )
        self.canvas_item_ids.extend([scr_up_id, scr_down_id])

        if not self.app.track_list:
            empty_id = self.app.bg_canvas.create_text(
                self.app.SCREEN_WIDTH // 2, 180, text="Empty Local Audio Catalog",
                font=("Courier New", 11, "bold"), fill="#000000", anchor="center"
            )
            self.canvas_item_ids.append(empty_id)
            return

        for index in range(self.visible_count):
            actual_track_index = index + self.scroll_offset
            y_pos = self.ROW_START_Y + (index * self.LINE_HEIGHT)
            
            if actual_track_index < len(self.app.track_list):
                track_name = self.app.track_list[actual_track_index]
                clean_display_title = track_name.replace(".mp3", "")
                
                # Truncated window adjusted for left-shifted coordinates alignment
                if len(clean_display_title) > 26:
                    clean_display_title = clean_display_title[:23] + "..."
                    
                display_string = f"[{actual_track_index + 1:02d}] {clean_display_title}"

                track_id = self.app.bg_canvas.create_text(
                    25, y_pos, text=display_string, font=("Courier New", 11, "bold"), fill="#000000", anchor="w"
                )
                self.canvas_item_ids.append(track_id)
                self.app.bg_canvas.itemconfig(track_id, tags=(f"track_{actual_track_index}", "track_item"))
            else:
                track_id = self.app.bg_canvas.create_text(
                    25, y_pos, text="", font=("Courier New", 11, "bold"), fill="#000000", anchor="w"
                )
                self.canvas_item_ids.append(track_id)

            line_y = y_pos + 12  
            divider_id = self.app.bg_canvas.create_line(
                self.LANE_X1, line_y, self.LANE_X2, line_y, fill="#D1D1D6", width=1
            )
            self.canvas_item_ids.append(divider_id)

    def on_canvas_click(self, event):
        clicked_item = self.app.bg_canvas.find_withtag("current")
        if not clicked_item: return
        tags = self.app.bg_canvas.gettags(clicked_item[0])
        
        if "back_btn" in tags:
            self.close_full_page_scroller()
            return
        
        if "ui_scroll_up" in tags:
            self.force_scroll_direction(-1)
            return
        if "ui_scroll_down" in tags:
            self.force_scroll_direction(1)
            return
            
        for tag in tags:
            if tag.startswith("track_") and tag != "track_item":
                if hasattr(self.app, 'play_ui_sound'):
                    self.app.play_ui_sound("click")
                track_index = int(tag.split("_")[1])
                self.app.current_track_index = track_index
                
                if self.app.shuffle_enabled:
                    self.app.generate_true_shuffle_queue()
                    
                self.app.play_current_track()
                break