import customtkinter as ctk

CTkFrame = {
    "width": 500,
    "height": 200,
    "corner_radius": 5,
    "border_width": 1,
    "fg_color": ["#F7F8FA", "#2B2D30"],
    "border_color": ["#D3D5DB", "#4E5157"]
}

CTkButton = {
    "width": 150,
    "height": 40,
    "corner_radius": 5,
    "border_width": 1,
    "fg_color": ["#3574F0", "#2B2D30"],
    "hover_color": ["#3369D6", "#4E5157"],
    "border_color": ["#C2D6FC", "#4E5157"],
    "text_color": ["#FFFFFF", "#DFE1E5"],
    "text_color_disabled": ["#A8ADBD", "#6F737A"]
}

CTkProgressBar = {
    "width": 460,
    "height": 5,
    "corner_radius": 5,
    "border_width": 0,
    "fg_color": ["#DFE1E5", "#43454A"],
    "progress_color": ["#3574F0", "#3574F0"],
    "border_color": ["#3574F0", "#4E5157"]
}

font_title = ("Inter", 20, "bold")
font_normal = ("Inter", 14, "normal")


class CTkLoader(ctk.CTkFrame):
    def __init__(self, parent: any, title: str, msg: str, cancel_func: any):
        super().__init__(master=parent, **CTkFrame)
        self.title = title.capitalize()
        self.msg = msg.capitalize()
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self.cancel_func = cancel_func

        title = ctk.CTkLabel(self, text=self.title, text_color=("#000000", "#DFE1E5"), font=font_title)
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")

        msg = ctk.CTkLabel(self, text=self.msg, text_color=("#000000", "#DFE1E5"), font=font_normal)
        msg.grid(row=1, column=0, padx=20, pady=10, sticky="nsw")

        self.progressbar = ctk.CTkProgressBar(self, mode="indeterminate", **CTkProgressBar)
        self.progressbar.grid(row=2, column=0, padx=20, pady=10, sticky="sw")
        self.progressbar.start()

        button = ctk.CTkButton(self, text="Cancel", command=self.cancel_callback, **CTkButton)
        button.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")

        # self.pack(anchor="center", expand=True)
        self.grid(row=0, column=0, sticky="ew", padx=20)

    def hide_loader(self):
        self.progressbar.stop()
        self.destroy()

    def cancel_callback(self):
        self.cancel_func()
        self.after(100, self.hide_loader)
