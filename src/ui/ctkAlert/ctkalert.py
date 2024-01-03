import os

import customtkinter as ctk
from PIL import Image

current_path = os.path.dirname(os.path.realpath(__file__))
icon_path = f"{current_path}{os.path.sep}icons{os.path.sep}"

icons = {
    "info": ctk.CTkImage(dark_image=Image.open(f"{icon_path}info_dark.png"),
                         light_image=Image.open(f"{icon_path}info_light.png"), size=(28, 28)),
    "success": ctk.CTkImage(dark_image=Image.open(f"{icon_path}success_dark.png"),
                            light_image=Image.open(f"{icon_path}success_light.png"), size=(28, 28)),
    "error": ctk.CTkImage(dark_image=Image.open(f"{icon_path}error_dark.png"),
                          light_image=Image.open(f"{icon_path}error_light.png"), size=(28, 28)),
    "warning": ctk.CTkImage(dark_image=Image.open(f"{icon_path}warning_dark.png"),
                            light_image=Image.open(f"{icon_path}warning_light.png"), size=(28, 28))
}

CTkFrame = {
    "width": 500,
    "height": 200,
    "corner_radius": 5,
    "border_width": 1,
    "fg_color": ["#F7F8FA", "#2B2D30"],
    "border_color": ["#D3D5DB", "#4E5157"]
}

CTkButton = {
    "width": 100,
    "height": 30,
    "corner_radius": 5,
    "border_width": 0,
    "fg_color": ["#3574F0", "#3574F0"],
    "hover_color": ["#3369D6", "#366ACF"],
    "border_color": ["#C2D6FC", "#4E5157"],
    "text_color": ["#FFFFFF", "#DFE1E5"],
    "text_color_disabled": ["#A8ADBD", "#6F737A"]
}

font_title = ("Inter", 20, "bold")
font_normal = ("Inter", 13, "normal")


class CTkAlert(ctk.CTkFrame):
    def __init__(self, parent: any, status: str, title: str, msg: str):
        super().__init__(master=parent, **CTkFrame)
        self.status = status
        self.title = title.capitalize()
        self.msg = msg.capitalize()
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text=f" {self.title}", image=icons.get(self.status, icons["info"]), compound="left",
                             text_color=("#000000", "#DFE1E5"), font=font_title)
        title.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        msg = ctk.CTkLabel(self, text=self.msg, text_color=("#000000", "#DFE1E5"), font=font_normal)
        msg.grid(row=1, column=0, padx=40, pady=20, sticky="nsew")

        button = ctk.CTkButton(self, text="OK", command=self.hide_alert, **CTkButton)
        button.grid(row=2, column=0, padx=20, pady=20, sticky="se")

        # self.pack(anchor="center", expand=True)
        self.grid(row=0, column=0, sticky="ew", padx=10)

    def hide_alert(self):
        self.destroy()
