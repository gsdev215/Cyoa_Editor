import customtkinter as ctk
from typing import TYPE_CHECKING, Union, Dict
from uuid import uuid4

from cyoa_io import THEME
from Editor.utility import Utility

if TYPE_CHECKING:
    from TkApp import CYOAMakerApplication as CYOAMaker


class Choice(Utility):
    def __init__(self, parent: 'CYOAMaker'):
        self.parent = parent
        self.root = parent.root
        self.default_font = parent.default_font
        self.choice = None

    def build_frame(
        self,
        parent: Union[ctk.CTkFrame, ctk.CTkScrollableFrame, None],
        choice: Dict,
        node: Dict,
        on_save_callback
    ) -> ctk.CTkFrame:
        self.choice = choice
        original_id = choice["id"]

        frame = ctk.CTkFrame(self.root, fg_color=THEME["bg_primary"])
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            frame,
            text="Choice Editor",
            font=("Segoe UI", 24, "bold"),
            text_color=THEME["accent"]
        )
        title.grid(row=0, column=0, pady=(10, 20), sticky="n")

        scrollable_frame = self._create_scrollable_frame(frame)
        self._configure_mousewheel(scrollable_frame)

        # Input Fields
        emoji_entry = self.create_labeled_input(
            scrollable_frame,
            label_text="Emoji",
            default_value=choice.get("emoji", ""),
            layout_options={"row": 0, "column": 0, "sticky": "ew", "padx": 10, "pady": 5},
            entry_width=10,
            component_config={
                "font": ctk.CTkFont("Noto Sans", 18, "bold"),
                "fg_color": THEME["bg_secondary"],
                "text_color": THEME["text_primary"],
                "border_color": THEME["accent"],
                "corner_radius": 8
            }
        )

        id_entry = self.create_labeled_input(
            scrollable_frame,
            label_text="ID:",
            default_value=original_id,
            layout_options={"row": 1, "column": 0, "sticky": "ew", "padx": 10, "pady": 5},
        )

        text_entry = self.create_text_area(
            scrollable_frame,
            label_text="Text:",
            default_value=choice.get("text", ""),
            row=3
        )

        script_entry = "" # maybe in future not sure why we will ever need this

        # Save button
        button_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        button_container.grid(row=6, column=0, pady=20)
        button_container.grid_columnconfigure((0, 1), weight=1)

        self.create_button_grid(
            button_container,
            text="Save",
            command=lambda: self._on_save(
                id_entry, emoji_entry, text_entry, script_entry, original_id, node
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

    def _on_save(self, id_entry, emoji_entry, text_entry, script_entry, original_id, node):
        new_id = id_entry.get().strip()
        updated_choice = {
            "id": new_id,
            "emoji": emoji_entry.get().strip(),
            "text": text_entry.get("0.0", "end").strip().replace('"', '“').replace("'", "′"),
            "script": script_entry
        }

        if new_id == original_id:
            for i, val in enumerate(node["choices"]):
                if val["id"] == original_id:
                    node["choices"][i] = updated_choice
                    break
        else:
            node["choices"].append(updated_choice)

        if new_id not in self.parent.story_map:
            self.parent.story_map[new_id] = {
                "id": new_id,
                "description": "",
                "script": "",
                "choices": [],
                "metadata": {}
            }

        self.parent.current_node_data = node
        self.parent._show_story_node_editor(node["id"])
