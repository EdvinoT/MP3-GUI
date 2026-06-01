import customtkinter as ctk
from tkinter import messagebox

class PlaylistManager:
    def __init__(self, main_app_instance):
        self.app = main_app_instance
        self.is_open = False
        self.canvas_playlist_ids = []

    def open_playlist_view(self):
        self.is_open = True
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")

        # Clear out all menu items
        self.app.btn_access.place_forget()
        if hasattr(self.app, 'btn_shuffle'):
            self.app.btn_shuffle.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_playlist.place_forget()
        
        if hasattr(self.app, 'btn_quick_settings'):
            self.app.btn_quick_settings.place_forget()
        self.app.btn_off.place_forget()

        if hasattr(self.app, 'playback_frame'):
            self.app.playback_frame.place_forget()
            
        self.app.progress_container.place_forget()
        self.app.controls_dock.place_forget()
        if self.app.timer_text_id:
            self.app.bg_canvas.itemconfig(self.app.timer_text_id, state="hidden")

        self.app.update_status_text("▪ PLAYLIST ENGINE ACTIVE ▪", color="#FFB300")
        self.render_playlist_screen()

    def render_playlist_screen(self):
        self.clear_playlist_canvas()

        # Create structural safety block across full screen
        shield_id = self.app.bg_canvas.create_rectangle(
            0, 0, self.app.SCREEN_WIDTH, self.app.SCREEN_HEIGHT,
            fill="", outline="", tags="playlist_click_shield"
        )
        self.canvas_playlist_ids.append(shield_id)
        self.app.bg_canvas.tag_bind(shield_id, "<Button-1>", lambda e: "break")

        # FIXED: Shifted back button hard-left to x=15 to match the sleek track scroller aesthetic!
        back_id = self.app.bg_canvas.create_text(
            15, 80, text="◀  BACK TO MAIN", 
            font=("Futura", 10, "bold"), fill="#FF5555", anchor="w", tags="playlist_back"
        )
        self.canvas_playlist_ids.append(back_id)
        self.app.bg_canvas.tag_bind(back_id, "<Button-1>", lambda e: self.close_playlist_view())

        # Aligned content information block nicely below the back button panel zone
        info_id = self.app.bg_canvas.create_text(
            85, 130, text="DEFAULT AUDIO QUEUE ACTIVE\nTRACK COUNT: " + str(len(self.app.track_list)),
            font=("Arial", 11, "bold"), fill="#000000", anchor="w"
        )
        self.canvas_playlist_ids.append(info_id)

    def close_playlist_view(self):
        self.is_open = False
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")

        self.clear_playlist_canvas()

        # Re-place main menu grid setup completely
        self.app.btn_access.place(x=60, y=140)
        if hasattr(self.app, 'btn_shuffle'):
            self.app.btn_shuffle.place(x=60, y=190)
        self.app.btn_add.place(x=260, y=140)
        self.app.btn_playlist.place(x=260, y=190)
        if hasattr(self.app, 'btn_quick_settings'):
            self.app.btn_quick_settings.place(x=15, y=266)
        self.app.btn_off.place(x=430, y=266)
        
        if hasattr(self.app, 'playback_frame'):
            self.app.playback_frame.place()
            
        self.app.progress_container.place(relx=0.5, y=252, anchor="center")
        self.app.controls_dock.place(relx=0.5, y=284, anchor="center")
        if self.app.timer_text_id:
            self.app.bg_canvas.itemconfig(self.app.timer_text_id, state="normal")

        if self.app.is_playing and self.app.track_list:
            track_name = self.app.track_list[self.app.current_track_index].replace(".mp3", "")
            self.app.update_status_text(f"▶ {track_name}", color="#FFB300")
        else:
            self.app.update_status_text("▪ ONLINE ▪", color="#888888")

    def clear_playlist_canvas(self):
        for cid in self.canvas_playlist_ids:
            self.app.bg_canvas.delete(cid)
        self.canvas_playlist_ids.clear()