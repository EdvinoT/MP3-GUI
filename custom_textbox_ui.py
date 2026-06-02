import customtkinter as ctk
import tkinter.messagebox as old_msg
import tkinter.simpledialog as old_dialog

class GlobalHardwarePopupEngine:
    def __init__(self):
        self.app = None
        self.input_buffer = ""
        self.input_submitted = False
        self.canvas_ids = []
        
        # Sleeker, clean hardware font configuration profiles
        self.FONT_HEADER = ("Helvetica Neue", 11, "normal")
        self.FONT_BODY = ("Helvetica Neue", 12, "normal")
        self.FONT_BUTTON = ("Helvetica Neue", 11, "normal")
        self.FONT_INPUT = ("Courier New", 13, "bold") # Preserved monospace clarity for typing

    def inject_hardware_patch(self, main_app_instance):
        """Hooks into the standard library calls and routes them to the canvas."""
        self.app = main_app_instance
        
        # Override the standard library references globally
        old_msg.askyesno = self.mock_askyesno
        old_msg.showinfo = self.mock_showinfo
        old_msg.showwarning = self.mock_showinfo  
        old_dialog.askstring = self.mock_askstring

    def _clear_popup_layers(self):
        for cid in self.canvas_ids:
            if self.app and hasattr(self.app, 'bg_canvas'):
                self.app.bg_canvas.delete(cid)
        self.canvas_ids.clear()

    def _draw_base_backdrop(self, title_text):
        self._clear_popup_layers()
        canvas = self.app.bg_canvas
        
        # Dimming backdrop shield
        shade = canvas.create_rectangle(0, 0, self.app.SCREEN_WIDTH, self.app.SCREEN_HEIGHT, fill="#0A0A0C", outline="", tags="global_popup")
        # Main dialog physical card block 
        card = canvas.create_rectangle(50, 60, 430, 260, fill="#131316", outline="#00A8FF", width=1, tags="global_popup")
        # Header block text string
        hdr = canvas.create_text(240, 88, text=str(title_text).upper(), font=self.FONT_HEADER, fill="#888888", tags="global_popup")
        
        self.canvas_ids.extend([shade, card, hdr])
        canvas.tag_bind(shade, "<Button-1>", lambda e: "break")
        
        # FIX: Push the backdrop elements to the front layer
        canvas.tag_raise("global_popup")

    # ---- MOCK: ASK YES / NO ----
    def mock_askyesno(self, title, message, **kwargs):
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
            
        self._draw_base_backdrop(title)
        canvas = self.app.bg_canvas
        
        msg_txt = canvas.create_text(240, 135, text=str(message), font=self.FONT_BODY, fill="#DDDDDD", justify="center", width=340, tags="global_popup")
        self.canvas_ids.append(msg_txt)

        user_choice = [False]
        loop_flag = ctk.BooleanVar(value=False)

        def click_action(response):
            user_choice[0] = response
            loop_flag.set(True)

        # Clean finger-target YES box
        b_yes = canvas.create_rectangle(80, 195, 230, 240, fill="#2A1414", outline="#FF5555", width=1, tags="global_popup")
        t_yes = canvas.create_text(155, 217, text="YES", font=self.FONT_BUTTON, fill="#FFAAAA", tags="global_popup")
        
        # Clean finger-target NO box
        b_no = canvas.create_rectangle(250, 195, 400, 240, fill="#1C1C22", outline="#555566", width=1, tags="global_popup")
        t_no = canvas.create_text(325, 217, text="NO", font=self.FONT_BUTTON, fill="#BBBBBB", tags="global_popup")

        self.canvas_ids.extend([b_yes, t_yes, b_no, t_no])

        for item in (b_yes, t_yes): canvas.tag_bind(item, "<Button-1>", lambda e: click_action(True))
        for item in (b_no, t_no): canvas.tag_bind(item, "<Button-1>", lambda e: click_action(False))

        # FIX: Ensure newly drawn buttons/text sit on top before freezing the loop
        canvas.tag_raise("global_popup")

        self.app.wait_variable(loop_flag)
        self._clear_popup_layers()
        return user_choice[0]

    # ---- MOCK: SHOW INFO / WARNING ----
    def mock_showinfo(self, title, message, **kwargs):
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
            
        self._draw_base_backdrop(title)
        canvas = self.app.bg_canvas

        msg_txt = canvas.create_text(240, 135, text=str(message), font=self.FONT_BODY, fill="#DDDDDD", justify="center", width=340, tags="global_popup")
        self.canvas_ids.append(msg_txt)

        loop_flag = ctk.BooleanVar(value=False)

        # Large "OK" confirmation touch area
        b_ok = canvas.create_rectangle(165, 195, 315, 240, fill="#1C1C22", outline="#00A8FF", width=1, tags="global_popup")
        t_ok = canvas.create_text(240, 217, text="OK", font=self.FONT_BUTTON, fill="#FFFFFF", tags="global_popup")
        self.canvas_ids.extend([b_ok, t_ok])

        for item in (b_ok, t_ok): canvas.tag_bind(item, "<Button-1>", lambda e: loop_flag.set(True))

        # FIX: Ensure newly drawn buttons/text sit on top before freezing the loop
        canvas.tag_raise("global_popup")

        self.app.wait_variable(loop_flag)
        self._clear_popup_layers()
        return "ok"

    # ---- MOCK: ASK STRING INPUT ----
    def mock_askstring(self, title, prompt, **kwargs):
        self._draw_base_backdrop(title)
        canvas = self.app.bg_canvas

        prompt_txt = canvas.create_text(240, 115, text=str(prompt), font=self.FONT_BODY, fill="#AAAAAA", tags="global_popup")
        
        # Variable display box field
        field = canvas.create_rectangle(80, 140, 400, 180, fill="#1C1C22", outline="#333344", width=1, tags="global_popup")
        
        self.input_buffer = ""
        text_render_id = canvas.create_text(240, 160, text="_", font=self.FONT_INPUT, fill="#00A8FF", tags="global_popup")
        
        self.canvas_ids.extend([prompt_txt, field, text_render_id])

        loop_flag = ctk.BooleanVar(value=False)
        self.input_submitted = False

        def stroke_listener(event):
            if event.keysym == "Return":
                self.input_submitted = True
                loop_flag.set(True)
            elif event.keysym == "Escape":
                self.input_submitted = False
                loop_flag.set(True)
            elif event.keysym == "BackSpace":
                self.input_buffer = self.input_buffer[:-1]
                canvas.itemconfig(text_render_id, text=self.input_buffer + "_")
            elif event.char and len(event.char) == 1 and (event.char.isalnum() or event.char in " _-"):
                if len(self.input_buffer) < 16:
                    self.input_buffer += event.char
                    canvas.itemconfig(text_render_id, text=self.input_buffer + "_")
            return "break"

        self.app.bind("<Key>", stroke_listener)

        # Confirm / Cancel buttons
        b_ent = canvas.create_rectangle(80, 205, 230, 248, fill="#122412", outline="#00FF00", width=1, tags="global_popup")
        t_ent = canvas.create_text(155, 226, text="ENTER", font=self.FONT_BUTTON, fill="#99FF99", tags="global_popup")
        
        b_cc = canvas.create_rectangle(250, 205, 400, 248, fill="#241212", outline="#FF5555", width=1, tags="global_popup")
        t_cc = canvas.create_text(325, 226, text="CANCEL", font=self.FONT_BUTTON, fill="#FFAAAA", tags="global_popup")
        
        self.canvas_ids.extend([b_ent, t_ent, b_cc, t_cc])

        for item in (b_ent, t_ent): canvas.tag_bind(item, "<Button-1>", lambda e: [setattr(self, 'input_submitted', True), loop_flag.set(True)])
        for item in (b_cc, t_cc): canvas.tag_bind(item, "<Button-1>", lambda e: [setattr(self, 'input_submitted', False), loop_flag.set(True)])

        # FIX: Ensure newly drawn input box elements sit on top before freezing the loop
        canvas.tag_raise("global_popup")

        self.app.wait_variable(loop_flag)
        self.app.unbind("<Key>")
        self._clear_popup_layers()

        return self.input_buffer.strip() if self.input_submitted else None

# Singleton configuration access instance hook
popup_engine = GlobalHardwarePopupEngine()