import json
import os
import customtkinter as ctk
from tkinter import messagebox, simpledialog

class PlaylistManager:
    def __init__(self, main_app_instance):
        self.app = main_app_instance
        self.is_open = False
        self.canvas_playlist_ids = []
        
        # Permanent hardware storage tracking file
        self.DATA_FILE = "playlists.json"
        
        # Automatically pull saved playlists from storage on boot
        self.load_playlists_from_disk()
        
        # Scroller navigation variables
        self.selection_mode = False
        self.editing_playlist_name = None
        self.selected_songs_pool = set() 
        self.scroll_offset = 0
        self.visible_count = 6 
        self.LINE_HEIGHT = 28
        self.ROW_START_Y = 130
        self.LANE_X1 = 85
        self.LANE_X2 = 465

    def save_playlists_to_disk(self):
        """Writes the custom playlists dictionary permanently to storage."""
        try:
            playlists_dict = getattr(self.app, 'custom_playlists', {})
            with open(self.DATA_FILE, "w") as f:
                json.dump(playlists_dict, f, indent=4)
        except Exception as e:
            print(f"Error saving playlists to storage: {e}")

    def load_playlists_from_disk(self):
        """Reads permanent playlists from storage back into application memory."""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r") as f:
                    self.app.custom_playlists = json.load(f)
            except Exception as e:
                print(f"Error loading playlists: {e}")
                self.app.custom_playlists = {}
        else:
            self.app.custom_playlists = {}

    def open_playlist_view(self):
        self.is_open = True
        self.selection_mode = False
        self.editing_playlist_name = None
        self.scroll_offset = 0
        
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")

        if not hasattr(self.app, 'all_local_tracks') or not self.app.all_local_tracks:
            self.app.all_local_tracks = list(self.app.track_list)

        # Hide main interface widgets
        self.app.btn_access.place_forget()
        if hasattr(self.app, 'btn_shuffle'):
            self.app.btn_shuffle.place_forget()
        self.app.btn_add.place_forget()
        self.app.btn_playlist.place_forget()
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

        # Touchscreen click shield
        shield_id = self.app.bg_canvas.create_rectangle(
            0, 0, self.app.SCREEN_WIDTH, self.app.SCREEN_HEIGHT,
            fill="", outline="", tags="playlist_click_shield"
        )
        self.canvas_playlist_ids.append(shield_id)
        self.app.bg_canvas.tag_bind(shield_id, "<Button-1>", lambda e: "break")

        if self.selection_mode:
            self.render_song_selection_scroller()
            return

        # ---- STANDARD MODE VIEW ----
        back_id = self.app.bg_canvas.create_text(
            15, 80, text="◀  BACK", 
            font=("Futura", 10, "bold"), fill="#FF5555", anchor="w", tags="playlist_back"
        )
        self.canvas_playlist_ids.append(back_id)
        self.app.bg_canvas.tag_bind(back_id, "<Button-1>", lambda e: self.close_playlist_view())

        create_id = self.app.bg_canvas.create_text(
            85, 120, text="[+ CREATE NEW LIST]",
            font=("Arial", 11, "bold"), fill="#00A8FF", anchor="w", tags="playlist_create"
        )
        self.canvas_playlist_ids.append(create_id)
        self.app.bg_canvas.tag_bind(create_id, "<Button-1>", lambda e: self.initiate_playlist_wizard(edit_mode=False))

        current_list_name = getattr(self.app, 'active_playlist_name', 'Main')
        status_str = f"ACTIVE LIST: {current_list_name.upper()}  ({len(self.app.track_list)} Tracks)"
        info_id = self.app.bg_canvas.create_text(
            85, 155, text=status_str, font=("Arial", 10, "bold"), fill="#000000", anchor="w"
        )
        self.canvas_playlist_ids.append(info_id)

        div_id = self.app.bg_canvas.create_line(85, 180, 465, 180, fill="#202025", width=1)
        self.canvas_playlist_ids.append(div_id)

        main_box_id = self.app.bg_canvas.create_text(
            85, 205, text="▶ PLAY ALL SONGS (MAIN CATALOG)",
            font=("Arial", 11, "bold"), fill="#000000", anchor="w", tags="play_all_trigger"
        )
        self.canvas_playlist_ids.append(main_box_id)
        self.app.bg_canvas.tag_bind(main_box_id, "<Button-1>", lambda e: self.action_activate_main_list())

        y_offset = 235
        playlists_dict = getattr(self.app, 'custom_playlists', {})
        
        if not playlists_dict:
            no_lists_id = self.app.bg_canvas.create_text(
                85, y_offset, text="(No custom playlists created yet)",
                font=("Arial", 10, "italic"), fill="#555555", anchor="w"
            )
            self.canvas_playlist_ids.append(no_lists_id)
        else:
            for p_name in list(playlists_dict.keys()):
                if y_offset > 300: break
                
                list_item_id = self.app.bg_canvas.create_text(
                    85, y_offset, text=f"▶ {p_name.upper()} ({len(playlists_dict[p_name])})",
                    font=("Arial", 11), fill="#000000", anchor="w"
                )
                self.canvas_playlist_ids.append(list_item_id)
                self.app.bg_canvas.tag_bind(list_item_id, "<Button-1>", lambda e, name=p_name: self.action_activate_custom_list(name))

                edit_btn_id = self.app.bg_canvas.create_text(
                    420, y_offset, text="[EDIT]",
                    font=("Arial", 10, "bold"), fill="#FFB300", anchor="e"
                )
                self.canvas_playlist_ids.append(edit_btn_id)
                self.app.bg_canvas.tag_bind(edit_btn_id, "<Button-1>", lambda e, name=p_name: self.initiate_playlist_wizard(edit_mode=True, name=name))
                
                y_offset += 24

    # ---- SCROLLER INTERACTIVE SELECTION MENU ENGINE ----
    def render_song_selection_scroller(self):
        self.app.unbind("<MouseWheel>")
        self.app.unbind("<Up>")
        self.app.unbind("<Down>")

        self.app.bind("<MouseWheel>", self.on_selection_scroll)
        self.app.bind("<Up>", lambda e: self.scroll_selection_list(-1))
        self.app.bind("<Down>", lambda e: self.scroll_selection_list(1))

        title_text = f"EDITING: {self.editing_playlist_name.upper()}" if self.editing_playlist_name else "NEW PLAYLIST SELECTION"
        title_id = self.app.bg_canvas.create_text(
            85, 55, text=title_text, font=("Arial", 11, "bold"), fill="#000000", anchor="w"
        )
        self.canvas_playlist_ids.append(title_id)

        cancel_id = self.app.bg_canvas.create_text(
            15, 90, text="[X] CANCEL", 
            font=("Futura", 10, "bold"), fill="#FF5555", anchor="w", tags="sel_cancel"
        )
        self.canvas_playlist_ids.append(cancel_id)
        self.app.bg_canvas.tag_bind(cancel_id, "<Button-1>", lambda e: self.exit_selection_scroller(save=False))

        save_id = self.app.bg_canvas.create_text(
            465, 90, text="[S] SAVE & EXIT", 
            font=("Futura", 10, "bold"), fill="#00A8FF", anchor="e", tags="sel_save"
        )
        self.canvas_playlist_ids.append(save_id)
        self.app.bg_canvas.tag_bind(save_id, "<Button-1>", lambda e: self.exit_selection_scroller(save=True))

        up_arrow = self.app.bg_canvas.create_text(395, 55, text="▲", font=("Arial", 10), fill="#555555", anchor="center")
        down_arrow = self.app.bg_canvas.create_text(435, 55, text="▼", font=("Arial", 10), fill="#555555", anchor="center")
        self.canvas_playlist_ids.extend([up_arrow, down_arrow])
        self.app.bg_canvas.tag_bind(up_arrow, "<Button-1>", lambda e: self.scroll_selection_list(-1))
        self.app.bg_canvas.tag_bind(down_arrow, "<Button-1>", lambda e: self.scroll_selection_list(1))

        available_tracks = getattr(self.app, 'all_local_tracks', [])
        if not available_tracks: return

        for index in range(self.visible_count):
            actual_track_idx = index + self.scroll_offset
            if actual_track_idx >= len(available_tracks): break

            y_pos = self.ROW_START_Y + (index * self.LINE_HEIGHT)
            track_filename = available_tracks[actual_track_idx]
            clean_title = track_filename.replace(".mp3", "")

            if len(clean_title) > 28:
                clean_title = clean_title[:25] + "..."

            is_checked = track_filename in self.selected_songs_pool
            check_box_char = "[X] " if is_checked else "[  ] "

            row_id = self.app.bg_canvas.create_text(
                85, y_pos, text=f"{check_box_char}{clean_title}",
                font=("Arial", 11), fill="#000000", anchor="w"
            )
            self.canvas_playlist_ids.append(row_id)

            self.app.bg_canvas.tag_bind(
                row_id, "<Button-1>", 
                lambda e, filename=track_filename: self.toggle_song_selection(filename)
            )

            line_y = y_pos + 13
            div_id = self.app.bg_canvas.create_line(self.LANE_X1, line_y, self.LANE_X2, line_y, fill="#202025", width=1)
            self.canvas_playlist_ids.append(div_id)

    def initiate_playlist_wizard(self, edit_mode=False, name=None):
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")

        if edit_mode:
            self.editing_playlist_name = name
            current_songs = self.app.custom_playlists.get(name, [])
            self.selected_songs_pool = set(current_songs)
        else:
            list_name = simpledialog.askstring("New Playlist", "Enter playlist name:", parent=self.app)
            if not list_name or list_name.strip() == "": return
            self.editing_playlist_name = list_name.strip()
            self.selected_songs_pool = set()

        self.selection_mode = True
        self.scroll_offset = 0
        self.render_playlist_screen()

    def toggle_song_selection(self, filename):
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("scroll")

        if filename in self.selected_songs_pool:
            self.selected_songs_pool.remove(filename)
        else:
            self.selected_songs_pool.add(filename)
        
        self.render_playlist_screen()

    def scroll_selection_list(self, direction):
        if direction == -1:
            self.scroll_offset = max(0, self.scroll_offset - 1)
        elif direction == 1:
            available_count = len(getattr(self.app, 'all_local_tracks', []))
            max_scroll = max(0, available_count - self.visible_count)
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
        
        self.render_playlist_screen()

    def on_selection_scroll(self, event):
        if event.delta and event.delta > 0:
            self.scroll_selection_list(-1)
        else:
            self.scroll_selection_list(1)

    def exit_selection_scroller(self, save=True):
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")

        self.app.unbind("<MouseWheel>")
        self.app.unbind("<Up>")
        self.app.unbind("<Down>")

        if save and self.editing_playlist_name:
            if not self.selected_songs_pool:
                messagebox.showwarning("Empty Selection", "Playlist must contain at least 1 song!")
                self.selection_mode = True
                self.render_playlist_screen()
                return
            
            if not hasattr(self.app, 'custom_playlists'):
                self.app.custom_playlists = {}
                
            self.app.custom_playlists[self.editing_playlist_name] = list(self.selected_songs_pool)
            
            # Commit the playlists to storage
            self.save_playlists_to_disk()
            
            messagebox.showinfo("Saved", f"Playlist '{self.editing_playlist_name}' updated successfully.")

        self.selection_mode = False
        self.editing_playlist_name = None
        self.selected_songs_pool.clear()
        self.scroll_offset = 0
        self.render_playlist_screen()

    def action_activate_main_list(self):
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
            
        if hasattr(self.app, 'all_local_tracks') and self.app.all_local_tracks:
            self.app.track_list = list(self.app.all_local_tracks)
            
        self.app.active_playlist_name = "Main"
        self.app.current_track_index = 0
        if hasattr(self.app, 'generate_true_shuffle_queue') and getattr(self.app, 'shuffle_enabled', False):
            self.app.generate_true_shuffle_queue()
            
        messagebox.showinfo("Active", "Active Playlist changed to: Main List")
        self.render_playlist_screen()

    def action_activate_custom_list(self, name):
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
            
        playlists_dict = getattr(self.app, 'custom_playlists', {})
        if name in playlists_dict:
            self.app.track_list = list(playlists_dict[name])
            self.app.active_playlist_name = name
            self.app.current_track_index = 0
            
            if hasattr(self.app, 'generate_true_shuffle_queue') and getattr(self.app, 'shuffle_enabled', False):
                self.app.generate_true_shuffle_queue()
                
            messagebox.showinfo("Active", f"Active Playlist changed to: '{name}'")
            self.render_playlist_screen()

    def close_playlist_view(self):
        self.is_open = False
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")

        self.clear_playlist_canvas()

        # Re-initialize standard layout interface positions
        self.app.btn_access.place(x=60, y=140)
        if hasattr(self.app, 'btn_shuffle'):
            self.app.btn_shuffle.place(x=60, y=190)
        self.app.btn_add.place(x=260, y=140)
        self.app.btn_playlist.place(x=260, y=190)
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