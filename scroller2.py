import os
import pygame

class TrackScroller:
    def __init__(self, main_app_instance):
        """
        Manages an overlay track selection scroll list layer on the shared canvas.
        Leaves the main menu title and subtitle visible at the top.
        """
        self.app = main_app_instance
        self.is_open = False
        self.active_track_idx = 0
        self.canvas_track_ids = []
        self.visible_rows = 5  # Number of songs to show at once on screen

    def toggle_full_page_scroller(self):
        if not self.app.track_list:
            self.app.update_status_text("▪ NO MP3 TRACKS DETECTED ▪", color="#FF3333")
            return

        self.is_open = True
        
        # CLEAN FIX: Explicitly hide ALL main menu buttons so nothing bleeds through
        self.app.btn_access.place_forget()
        self.app.btn_shuffle.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_settings.place_forget()  # Fixed: Settings button now disappears cleanly
        self.app.btn_off.place_forget()       # Fixed: Shutdown button now disappears cleanly
        
        # Hide the lower media playback dock UI components
        self.app.playback_frame.place_forget()
        self.app.progress_container.place_forget()
        self.app.controls_dock.place_forget()
        if self.app.timer_text_id:
            self.app.bg_canvas.itemconfig(self.app.timer_text_id, state="hidden")

        # Automatically synchronize selector index to currently active audio index track
        self.active_track_idx = self.app.current_track_index
        self.app.update_status_text("▪ SELECT LOCAL TRACK MODULE ▪", color="#00A8FF")
        self.render_scroll_view()

        # Keyboard emulation hooks for encoder wheels/dials navigation testing
        self.app.bind("<Key-u>", lambda e: self._navigate_scroll(-1))
        self.app.bind("<Key-d>", lambda e: self._navigate_scroll(1))
        self.app.bind("<Return>", lambda e: self._confirm_selection())

    def render_scroll_view(self):
        # Flush previously drawn canvas rendering items to prevent visual stacking
        for cid in self.canvas_track_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_track_ids.clear()

        # Back Navigation Arrow Label
        back_id = self.app.bg_canvas.create_text(
            45, 135, text="◀  RETURN TO MAIN", 
            font=("Futura", 10, "bold"), fill="#FF5555", anchor="w", tags="back_btn"
        )
        self.canvas_track_ids.append(back_id)
        self.app.bg_canvas.tag_bind(back_id, "<Button-1>", lambda e: self.close_track_scroller())

        # Determine dynamic paging offsets so our window slides with selection index pointer
        start_idx = max(0, self.active_track_idx - (self.visible_rows // 2))
        if start_idx + self.visible_rows > len(self.app.track_list):
            start_idx = max(0, len(self.app.track_list) - self.visible_rows)

        end_idx = min(start_idx + self.visible_rows, len(self.app.track_list))

        # Render list window lines
        for display_slot, track_idx in enumerate(range(start_idx, end_idx)):
            y_pos = 175 + (display_slot * 26)  # Distributed line spacing down the page coordinate
            
            raw_filename = self.app.track_list[track_idx]
            clean_name = raw_filename.replace(".mp3", "").upper()
            
            # Format text line view presentation string truncation
            if len(clean_name) > 36:
                clean_name = clean_name[:33] + "..."
                
            display_text = f"{track_idx + 1:02d}. {clean_name}"
            
            # Highlight currently selected line profile item link pointer index
            color = "#00A8FF" if track_idx == self.active_track_idx else "#FFFFFF"
            
            t_id = self.app.bg_canvas.create_text(
                45, y_pos, text=display_text, font=("Arial", 11, "bold"), fill=color, anchor="w", tags="track_item"
            )
            self.canvas_track_ids.append(t_id)

            # Bind immediate hardware click indexing hook properties to track item lines
            self.app.bg_canvas.tag_bind(
                t_id, 
                "<Button-1>", 
                lambda e, idx=track_idx: [self._set_active_track(idx), self._confirm_selection()]
            )

    def _set_active_track(self, idx):
        self.active_track_idx = idx
        self.render_scroll_view()

    def _navigate_scroll(self, direction):
        if not self.app.track_list: return
        self.app.play_ui_sound("scroll")
        self.active_track_idx = (self.active_track_idx + direction) % len(self.app.track_list)
        self.render_scroll_view()

    def _confirm_selection(self):
        if not self.app.track_list: return
        self.app.play_ui_sound("click")
        
        # Push selected pointer index down to playback machine core tracker register
        self.app.current_track_index = self.active_track_idx
        
        # Reset shuffle engine tracking queues if user explicitly breaks queue line choice manually
        if self.app.shuffle_enabled:
            self.app.generate_true_shuffle_queue()
            
        self.app.play_current_track()
        self.close_track_scroller()

    def close_track_scroller(self):
        self.is_open = False
        self.app.play_ui_sound("click")
        
        # Clear line assets from UI layout view canvas stacking layers
        for cid in self.canvas_track_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_track_ids.clear()

        # Release context listeners safely
        self.app.unbind("<Key-u>")
        self.app.unbind("<Key-d>")
        self.app.unbind("<Return>")

        # Restore ALL main layout navigation objects cleanly to coordinate spaces
        self.app.btn_access.place(x=60, y=140)
        self.app.btn_shuffle.place(x=60, y=190)
        self.app.btn_add.place(x=260, y=140)
        self.app.btn_settings.place(x=260, y=190)  # Restored perfectly
        self.app.btn_off.place(x=15, y=266)         # Restored perfectly
        self.app.playback_frame.place()
        
        # Reset active string configuration text settings profile
        if self.app.is_playing:
            track_name = self.app.track_list[self.app.current_track_index].replace(".mp3", "")
            self.app.update_status_text(f"▶ {track_name}", color="#FFB300")
        else:
            self.app.update_status_text("▪ ONLINE ▪", color="#888888")