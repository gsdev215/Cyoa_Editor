from emojiSchema import EmojiSchema
from typing import TYPE_CHECKING
from cyoa_io import THEME
from Editor.utility import Utility
import customtkinter as ctk

if TYPE_CHECKING:
    from TkApp import CYOAMakerApplication as CYOAMaker


class EmojiEditor(Utility):
    def __init__(self, parent: 'CYOAMaker'):
        self.parent = parent
        self.root = parent.root
        self.default_font = parent.default_font

    def build_frame(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.root, fg_color=THEME["bg_primary"])
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=0)  # Title
        frame.grid_rowconfigure(1, weight=1)  # Content
        frame.grid_rowconfigure(2, weight=0)  # Button
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text="Emoji Editor",
            font=("Segoe UI", 24, "bold"),
            text_color=THEME["accent"]
        ).grid(row=0, column=0, pady=(10, 20), sticky="n")

        default_text = self.parent.emoji_schema.current_schema

        content = self.create_text_area(
            frame,
            label_text="Emoji Text",
            default_value=default_text,
            height=20,
            component_config={"font": ("Segoe UI Emoji", 20)},
        )

        self.create_button_grid(
            frame,
            text="Save",
            command=lambda: self.save_emoji(content.get("1.0", "end-1c")),
            row=2,
            width=150,
            column=0,
        )

        return frame

    def save_emoji(self, content: str) -> None:
        self.parent.emoji_schema.current_schema = content
        self.parent._show_main_menu()
