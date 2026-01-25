import customtkinter as ctk
from typing import TYPE_CHECKING, Union, Dict
from uuid import uuid4

from cyoa_io import THEME
from Editor.utility import Utility
from cyoa_io import Metadata as metadata_formate
if TYPE_CHECKING:
    from TkApp import CYOAMakerApplication as CYOAMaker


class Metadata(Utility):
    def __init__(self, parent: 'CYOAMaker'):
        self.parent = parent
        self.root = parent.root
        self.default_font = parent.default_font
        self.choice = None

    def build_frame(
        self
    ) -> ctk.CTkFrame:

        frame = ctk.CTkFrame(self.root, fg_color=THEME["bg_primary"])
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            frame,
            text="Metadata Editor",
            font=("Segoe UI", 24, "bold"),
            text_color=THEME["accent"]
        )
        title.grid(row=0, column=0, pady=(10, 20), sticky="n")

        scrollable_frame = self._create_scrollable_frame(frame)
        self._configure_mousewheel(scrollable_frame)

        fields_dict = self.parent.metadata._asdict()

        author = self.create_labeled_input(
            scrollable_frame,
            label_text="Author:",
            default_value=fields_dict["Author"],
            layout_options={"row": 0, "column": 0, "sticky": "ew", "padx": 10, "pady": 5},
        )

        Name = self.create_labeled_input(
            scrollable_frame,
            label_text="Title:",
            default_value=fields_dict['name'],
            layout_options={"row": 1, "column": 0, "sticky": "ew", "padx": 10, "pady": 5},
        )

        Cyoa_id = self.create_labeled_input(
            scrollable_frame,
            label_text="Cyoa ID:",
            default_value=fields_dict['id'],
            layout_options={"row": 2, "column": 0, "sticky": "ew", "padx": 10, "pady": 5},

        )

        description = self.create_text_area(
            scrollable_frame,
            label_text='Description:',
            default_value=fields_dict["description"],
            row = 4,
            column= 0
        )

        start_node_id = self.create_labeled_input(
            scrollable_frame,
            label_text="Starting Node ID:",
            default_value=fields_dict["start"],
            layout_options={"row": 5, "column": 0, "sticky": "ew", "padx": 10, "pady": 5}
        )

        footer = self.create_labeled_input(
            scrollable_frame,
            label_text="Footer:",
            default_value=fields_dict["footer"],
            layout_options={"row": 6, "column": 0, "sticky": "ew", "padx": 10, "pady": 5}
        )
        button_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        button_container.grid(row=6, column=0, pady=20)
        button_container.grid_columnconfigure((0, 1), weight=1)

        self.create_button_grid(
            button_container,
            text="Save",
            command=lambda: self._on_save(
                author,
                Name,
                Cyoa_id,
                description,
                start_node_id,
                footer
            ),
            row=0,
            width=150,
            column=0
        )

        return frame


    def _create_scrollable_frame(self, parent) -> ctk.CTkScrollableFrame:
        frame = ctk.CTkScrollableFrame(
            parent,
            fg_color=THEME["bg_primary"],
            width=700,
            height=600,
            corner_radius=12
        )
        frame.grid(row=1, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        return frame

    def _configure_mousewheel(self, scrollable_frame: ctk.CTkScrollableFrame):
        def _on_mousewheel(event):
            direction = -int(event.delta / 120) if hasattr(event, "delta") else (
                -1 if getattr(event, "num", None) == 4 else 1
            )
            scrollable_frame._parent_canvas.yview_scroll(direction, "units")
            return "break"

        scrollable_frame.bind("<Enter>", lambda e: scrollable_frame._parent_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        scrollable_frame.bind("<Leave>", lambda e: scrollable_frame._parent_canvas.unbind_all("<MouseWheel>"))
        scrollable_frame.bind("<Destroy>", lambda e: scrollable_frame._parent_canvas.unbind_all("<MouseWheel>"))


    def _on_save(self,author,name,node_id,description,starting_node_id,footer):
        self.parent.metadata = metadata_formate(
            Author=author,
            name=name,
            id=node_id,
            description=description,
            start=starting_node_id,
            tag=[],
            footer=footer
        )
