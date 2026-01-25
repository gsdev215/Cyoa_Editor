from typing import TYPE_CHECKING
from cyoa_io import THEME
from Editor.utility import Utility
import customtkinter as ctk

if TYPE_CHECKING:
    from TkApp import CYOAMakerApplication as CYOAMaker


class Chardata(Utility):
    def __init__(self, parent: 'CYOAMaker'):
        self.parent = parent
        self.root = parent.root
        self.default_font = parent.default_font

    def build_frame(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.root, fg_color=THEME["bg_primary"])
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text="Emoji Editor",
            font=("Segoe UI", 24, "bold"),
            text_color=THEME["accent"]
        ).grid(row=0, column=0, pady=(10, 20), sticky="n")

        scrollable_frame = ctk.CTkScrollableFrame(
            frame,
            fg_color=THEME["bg_primary"],
            width=700,
            height=600,
            corner_radius=12
        )
        scrollable_frame.grid(row=1, column=0, sticky="nsew")
        scrollable_frame.grid_columnconfigure(0, weight=1)

        # Cross-platform scroll support
        def _on_mousewheel(event):
            delta = -int(event.delta / 120) if hasattr(event, "delta") else (1 if event.num == 5 else -1)
            scrollable_frame._parent_canvas.yview_scroll(delta, "units")
            return "break"

        scrollable_frame.bind("<Enter>", lambda e: scrollable_frame._parent_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        scrollable_frame.bind("<Leave>", lambda e: scrollable_frame._parent_canvas.unbind_all("<MouseWheel>"))
        scrollable_frame.bind("<Destroy>", lambda e: scrollable_frame._parent_canvas.unbind_all("<MouseWheel>"))

        entries = self._generate_entries(scrollable_frame)

        def on_save():
            for entry_name, entry in entries:
                self.parent.player_data[entry_name] = entry.get()

        # Button container
        button_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        button_container.grid(row=len(entries) + 2, column=0, pady=20)
        button_container.grid_columnconfigure((0, 1), weight=1)

        self.create_button_grid(
            button_container,
            text="Save",
            command=on_save,
            row=0,
            width=150,
            column=0
        )

        return frame

    def _generate_entries(self, parent_frame: ctk.CTkScrollableFrame):
        """Helper to generate and return labeled entry widgets."""
        entries = []
        for i, key in enumerate(self.parent.player_data):
            entry = self.create_labeled_input(
                parent_frame,
                label_text=key,
                default_value=self.parent.player_data[key],
                layout_options={"row": i + 2, "padx": 10, "pady": 10},
            )
            entries.append((key, entry))
        return entries

    def refresh_entries(self, parent_frame: ctk.CTkScrollableFrame):
        for widget in parent_frame.winfo_children():
            widget.destroy()
        return self._generate_entries(parent_frame)