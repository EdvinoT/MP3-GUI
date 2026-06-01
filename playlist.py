import customtkinter as ctk
from tkinter import messagebox, simpledialog

class PlaylistManager:
    def __init__(self, main_app_instance):
        self.app = main_app_instance
        self.is_open = False
        self.canvas_playlist_ids = []

    def open_playlist_view(self):
        self.is_open = True
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")

        # Back up the master track list if we haven't already
        if not hasattr(self.app, 'all_local_tracks') or not self.app.all_local_tracks:
            self.app.all_local_tracks = list(self.app.track_list)

        # Clear out main menu buttons
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

        # Invisible safety click block over total screen space
        shield_id = self.app.bg_canvas.create_rectangle(
            0, 0, self.app.SCREEN_WIDTH, self.app.SCREEN_HEIGHT,
            fill="", outline="", tags="playlist_click_shield"
        )
        self.canvas_playlist_ids.append(shield_id)
        self.app.bg_canvas.tag_bind(shield_id, "<Button-1>", lambda e: "break")

        # Sleek hard-left Back Button (x=15)
        back_id = self.app.bg_canvas.create_text(
            15, 80, text="◀  BACK TO MAIN", 
            font=("Futura", 10, "bold"), fill="#FF5555", anchor="w", tags="playlist_back"
        )
        self.canvas_playlist_ids.append(back_id)
        self.app.bg_canvas.tag_bind(back_id, "<Button-1>", lambda e: self.close_playlist_view())

        # [+ CREATE NEW LIST] Button (Staggered layout at x=85)
        create_id = self.app.bg_canvas.create_text(
            85, 120, text="[+ CREATE NEW LIST]",
            font=("Arial", 11, "bold"), fill="#00A8FF", anchor="w", tags="playlist_create"
        )
        self.canvas_playlist_ids.append(create_id)
        self.app.bg_canvas.tag_bind(create_id, "<Button-1>", lambda e: self.action_create_playlist())

        # Render Active Status Box
        current_list_name = getattr(self.app, 'active_playlist_name', 'Main')
        status_str = f"ACTIVE LIST: {current_list_name.upper()}\nTRACKS: {len(self.app.track_list)}"
        info_id = self.app.bg_canvas.create_text(
            85, 160, text=status_str,
            font=("Arial", 10, "bold"), fill="#000000", anchor="w"
        )
        self.canvas_playlist_ids.append(info_id)

        # Draw a divider line
        div_id = self.app.bg_canvas.create_line(85, 195, 465, 195, fill="#202025", width=1)
        self.canvas_playlist_ids.append(div_id)

        # List Selection Options
        # Option A: Restore/Play All Songs (Main Catalog)
        main_box_id = self.app.bg_canvas.create_text(
            85, 220, text="▶ PLAY ALL SONGS (MAIN CATALOG)",
            font=("Arial", 11, "bold"), fill="#000000", anchor="w", tags="play_all_trigger"
        )
        self.canvas_playlist_ids.append(main_box_id)
        self.app.bg_canvas.tag_bind(main_box_id, "<Button-1>", lambda e: self.action_activate_main_list())

        # Option B: Custom Lists List-out Display
        y_offset = 250
        playlists_dict = getattr(self.app, 'custom_playlists', {})
        
        if not playlists_dict:
            no_lists_id = self.app.bg_canvas.create_text(
                85, y_offset, text="(No custom playlists created yet)",
                font=("Arial", 10, "italic"), fill="#555555", anchor="w"
            )
            self.canvas_playlist_ids.append(no_lists_id)
        else:
            for p_name in list(playlists_dict.keys()):
                if y_offset > 300: break # Keep within screen safety bounds
                
                display_text = f"⚙ LIST: {p_name.upper()} ({len(playlists_dict[p_name])} Tracks)"
                
                list_item_id = self.app.bg_canvas.create_text(
                    85, y_offset, text=display_text,
                    font=("Arial", 11), fill="#212124", anchor="w", tags=f"load_list_{p_name}"
                )
                self.canvas_playlist_ids.append(list_item_id)
                
                # Bind item to instantly swap active playback array context
                self.app.bg_canvas.tag_bind(
                    list_item_id, "<Button-1>", lambda e, name=p_name: self.action_activate_custom_list(name)
                )
                y_offset += 25

    def action_create_playlist(self):
        """Asks for a name and lets the user pick songs to build a playlist loop."""
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
            
        list_name = simpledialog.askstring("New Playlist", "Enter playlist name:", parent=self.app)
        if not list_name or list_name.strip() == "": return
        list_name = list_name.strip()

        # Gather track choices using standard multi-select dialog prompt context
        available_tracks = getattr(self.app, 'all_local_tracks', list(self.app.track_list))
        if not available_tracks:
            messagebox.showwarning("Empty", "No songs found in local catalog folder.")
            return

        selected_tracks = []
        for track in available_tracks:
            clean_title = track.replace(".mp3", "")
            ans = messagebox.askyesno("Add Song?", f"Add to '{list_name}':\n{clean_title}?")
            if ans:
                selected_tracks.append(track)

        if not selected_tracks:
            messagebox.showinfo("Cancelled", "Playlist must have at least 1 track.")
            return

        if not hasattr(self.app, 'custom_playlists'):
            self.app.custom_playlists = {}
            
        self.app.custom_playlists[list_name] = selected_tracks
        messagebox.showinfo("Success", f"Playlist '{list_name}' created successfully!")
        self.render_playlist_screen()

    def action_activate_main_list(self):
        """Restores the track array context to load all music inventory elements."""
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
            
        if hasattr(self.app, 'all_local_tracks') and self.app.all_local_tracks:
            self.app.track_list = list(self.app.all_local_tracks)
            
        self.app.active_playlist_name = "Main"
        self.app.current_track_index = 0
        if hasattr(self.app, 'generate_true_shuffle_queue') and getattr(self.app, 'shuffle_enabled', False):
            self.app.generate_true_shuffle_queue()
            
        messagebox.showinfo("Active", "Switched back to Main List (All Tracks)")
        self.render_playlist_screen()

    def action_activate_custom_list(self, name):
        """Swaps playback tracking references to strictly lock loops inside a chosen list."""
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
            
        playlists_dict = getattr(self.app, 'custom_playlists', {})
        if name in playlists_dict:
            # Back up main inventory array if missing
            if not hasattr(self.app, 'all_local_tracks') or not self.app.all_local_tracks:
                self.app.all_local_tracks = list(self.app.track_list)
                
            self.app.track_list = list(playlists_dict[name])
            self.app.active_playlist_name = name
            self.app.current_track_index = 0
            
            if hasattr(self.app, 'generate_true_shuffle_queue') and getattr(self.app, 'shuffle_enabled', False):
                self.app.generate_true_shuffle_queue()
                
            messagebox.showinfo("Active", f"Now playing only from playlist: '{name}'")
            self.render_playlist_screen()

    def close_playlist_view(self):
        self.is_open = False
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")

        self.clear_playlist_canvas()

        # Re-place main menu setup precisely
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