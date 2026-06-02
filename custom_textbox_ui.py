import customtkinter as ctk
import tkinter.messagebox as old_msg
import tkinter.simpledialog as old_dialog

class GlobalHardwarePopupEngine:
    def __init__(self):
        self.app = None
        self.input_buffer = ""
        self.input_submitted = False
        
        self.FONT_HEADER = ("Helvetica Neue", 11, "normal")
        self.FONT_BODY = ("Helvetica Neue", 12, "normal")
        self.FONT_BUTTON = ("Helvetica Neue", 11, "normal")
        self.FONT_INPUT = ("Courier New", 13, "bold")

    def inject_hardware_patch(self, main_app_instance):
        self.app = main_app_instance
        old_msg.askyesno = self.mock_askyesno
        old_msg.showinfo = self.mock_showinfo
        old_msg.showwarning = self.mock_showinfo  
        old_dialog.askstring = self.mock_askstring

    def _create_popup_window(self, title_text):
        """Creates a truly modal, borderless window over the app center"""
        popup = ctk.CTkToplevel(self.app)
        popup.overrideredirect(True) # Removes window borders and top bar
        
        # Center the popup window over your fixed hardware dimensions
        w, h = 380, 200
        x = self.app.winfo_x() + (self.app.winfo_width() // 2) - (w // 2)
        y = self.app.winfo_y() + (self.app.winfo_height() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")
        
        # Styling matching your dark hardware theme
        popup.configure(fg_color="#131316")
        
        # Border emulation
        border_frame = ctk.CTkFrame(popup, fg_color="#131316", border_color="#00A8FF", border_width=1)
        border_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Header Label
        hdr = ctk.CTkLabel(border_frame, text=str(title_text).upper(), font=self.FONT_HEADER, text_color="#888888")
        hdr.pack(pady=(15, 5))
        
        # Set focus and freeze main app interaction until closed
        popup.grab_set()
        return popup, border_frame

    # ---- MOCK: SHOW INFO / WARNING ----
    def mock_showinfo(self, title, message, **kwargs):
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
            
        popup, frame = self._create_popup_window(title)
        loop_flag = ctk.BooleanVar(value=False)

        # Message Text
        msg_txt = ctk.CTkLabel(frame, text=str(message), font=self.FONT_BODY, text_color="#DDDDDD", wraplength=320)
        msg_txt.pack(pady=(10, 20))

        # OK button configured to match your custom dimensions
        b_ok = ctk.CTkButton(
            frame, width=150, height=45, text="OK", font=self.FONT_BUTTON,
            fg_color="#1C1C22", text_color="#FFFFFF", border_color="#00A8FF", border_width=1,
            hover_color="#25252D", command=lambda: loop_flag.set(True)
        )
        b_ok.pack(pady=(0, 15))

        self.app.wait_variable(loop_flag)
        popup.destroy()
        return "ok"

    # ---- MOCK: ASK YES / NO ----
    def mock_askyesno(self, title, message, **kwargs):
        if hasattr(self.app, 'play_ui_sound'):
            self.app.play_ui_sound("click")
            
        popup, frame = self._create_popup_window(title)
        user_choice = [False]
        loop_flag = ctk.BooleanVar(value=False)

        msg_txt = ctk.CTkLabel(frame, text=str(message), font=self.FONT_BODY, text_color="#DDDDDD", wraplength=320)
        msg_txt.pack(pady=(10, 20))

        btn_container = ctk.CTkFrame(frame, fg_color="transparent")
        btn_container.pack(fill="x", padx=30)

        def click_action(response):
            user_choice[0] = response
            loop_flag.set(True)

        b_yes = ctk.CTkButton(btn_container, width=140, height=45, text="YES", font=self.FONT_BUTTON, fg_color="#2A1414", text_color="#FFAAAA", border_color="#FF5555", border_width=1, command=lambda: click_action(True))
        b_yes.pack(side="left", expand=True, padx=5)

        b_no = ctk.CTkButton(btn_container, width=140, height=45, text="NO", font=self.FONT_BUTTON, fg_color="#1C1C22", text_color="#BBBBBB", border_color="#555566", border_width=1, command=lambda: click_action(False))
        b_no.pack(side="right", expand=True, padx=5)

        self.app.wait_variable(loop_flag)
        popup.destroy()
        return user_choice[0]

    # ---- MOCK: ASK STRING INPUT ----
    def mock_askstring(self, title, prompt, **kwargs):
        popup, frame = self._create_popup_window(title)
        loop_flag = ctk.BooleanVar(value=False)
        self.input_submitted = False

        prompt_txt = ctk.CTkLabel(frame, text=str(prompt), font=self.FONT_BODY, text_color="#AAAAAA")
        prompt_txt.pack(pady=(5, 5))

        # Replaces custom key hooks with a clean CustomTkinter Entry widget
        entry = ctk.CTkEntry(frame, width=320, height=40, font=self.FONT_INPUT, fg_color="#1C1C22", text_color="#00A8FF", border_color="#333344", justify="center")
        entry.pack(pady=(0, 15))
        entry.focus_set()

        btn_container = ctk.CTkFrame(frame, fg_color="transparent")
        btn_container.pack(fill="x", padx=30)

        def submit(status):
            self.input_submitted = status
            self.input_buffer = entry.get()
            loop_flag.set(True)

        popup.bind("<Return>", lambda e: submit(True))
        popup.bind("<Escape>", lambda e: submit(False))

        b_ent = ctk.CTkButton(btn_container, width=140, height=43, text="ENTER", font=self.FONT_BUTTON, fg_color="#122412", text_color="#99FF99", border_color="#00FF00", border_width=1, command=lambda: submit(True))
        b_ent.pack(side="left", expand=True, padx=5)
        
        b_cc = ctk.CTkButton(btn_container, width=140, height=43, text="CANCEL", font=self.FONT_BUTTON, fg_color="#241212", text_color="#FFAAAA", border_color="#FF5555", border_width=1, command=lambda: submit(False))
        b_cc.pack(side="right", expand=True, padx=5)

        self.app.wait_variable(loop_flag)
        popup.destroy()
        return self.input_buffer.strip() if self.input_submitted else None

popup_engine = GlobalHardwarePopupEngine()