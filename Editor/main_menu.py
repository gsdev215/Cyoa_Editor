import customtkinter as ctk
from typing import TYPE_CHECKING, Union, Dict
from uuid import uuid4

from cyoa_io import THEME ,tags
from Editor.utility import Utility
from Editor.tags_edit import SmartDropdown 
if TYPE_CHECKING:
    from TkApp import CYOAMakerApplication as CYOAMaker


class MainMenu(Utility):
    def __init__(self, parent: 'CYOAMaker'):
        self.parent = parent
        self.root = parent.root
        self.default_font = parent.default_font
        self.choice = None
        self.sd : SmartDropdown = None # type: ignore
        self.selected_tags = []  # Store selected tags

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

        title_entry = self.create_labeled_input(
            scrollable_frame, 
            label_text="Title:", 
            default_value=self.parent.metadata.name, 
            layout_options={"row": 0, "column": 0, "sticky": "ew", "padx": 10, "pady": 5})
        
        author_entry = self.create_labeled_input(
            scrollable_frame,
            label_text="Author:", 
            default_value=self.parent.metadata.Author, 
            layout_options={"row": 1, "column": 0, "sticky": "ew", "padx": 10, "pady": 5})
        
        id_entry = self.create_labeled_input(
            scrollable_frame,
            label_text="ID:",
            default_value=self.parent.metadata.id,
            layout_options={"row": 2, "column": 0, "sticky": "ew", "padx": 10, "pady": 5},
        )

        description_entry = self.create_text_area(
            scrollable_frame,
            "Description",
            default_value=self.parent.metadata.description,
            use_pack=False,
            row=3
        )

        starting_node_id = self.create_labeled_input(
            scrollable_frame,
            label_text="Starting node ID:",
            default_value=self.parent.metadata.start if self.parent.metadata.start != "" else "1",
            layout_options={"row": 4, "column": 0, "sticky": "ew", "padx": 10, "pady": 5},
        )

        self.tags_entry = self.create_labeled_input(
            scrollable_frame,
            label_text="Tags:",
            default_value= "".join(self.parent.metadata.tag) if self.parent.metadata.tag != [""] else "fantasy",
            layout_options={"row": 5, "column": 0, "sticky": "ew", "padx": 10, "pady": 5},
        )
        self.tags_entry.configure(state="readonly")

        footer_entry = self.create_labeled_input(
            scrollable_frame,
            label_text="Footer:",
            default_value=self.parent.metadata.footer,
            layout_options={"row": 6, "column": 0, "sticky": "ew", "padx": 10, "pady": 5},
        )

        btn = self.create_button_grid(
            scrollable_frame,
            text="Edit Tags",
            command=self.open_tags_edit,
            row=5,
            width=150,
            column=1
        )

        button_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        button_container.grid(row=7, column=0, pady=20)
        button_container.grid_columnconfigure((0, 1), weight=1)

        def on_save():
            self.parent.metadata.name = title_entry.get()
            self.parent.metadata.Author = author_entry.get()
            self.parent.metadata.id = id_entry.get()
            self.parent.metadata.description = description_entry.get("1.0", "end-1c").replace('"', '“').replace("'", "′")
            self.parent.metadata.start = starting_node_id.get()
            self.parent.player_data["StartID"] = starting_node_id.get()
            self.parent.player_data["currentID"] = starting_node_id.get()
            self.parent.metadata.tag = self.tags_entry.get().split(",")
            self.parent.metadata.footer = footer_entry.get()
            sv.configure(text="Saved",fg_color="green")
            self._on_save()

        sv = self.create_button_grid(
            button_container,
            text="Save",
            command= on_save,
            row=0,
            width=150,
            column=0
        )

        self.create_button_grid(
            button_container,
            text="Back",
            command=self.parent._show_main_menu,
            row=0,
            width=150,
            column=1
        )
        return frame
    
    def open_tags_edit(self):
        def on_selection_changed(selected_items):
            print(f"Selection changed: {selected_items}")
            self.selected_tags = selected_items
        
        # Create a popup window
        popup = ctk.CTkToplevel(self.root)
        popup.title("Edit Tags")
        popup.geometry("500x600")
        popup.transient(self.root)  # Make it a child of the main window
        popup.grab_set()  # Make it modal
        
        # Center the popup on the main window
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        
        # Create the SmartDropdown inside the popup
        self.sd = SmartDropdown(
            popup,
            values=tags,
            placeholder="Search tags...",
            max_results=10,
            allow_duplicates=False,
            case_sensitive=False,
            on_selection_change=on_selection_changed
        )
        self.sd.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Set any existing selected tags
        if self.selected_tags:
            self.sd.set_selected(self.selected_tags)
        # Add OK and Cancel buttons
        button_frame = ctk.CTkFrame(popup, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def on_ok():
            self.selected_tags = self.sd.get_selected()
            self.parent.metadata.tag = self.selected_tags
            self.tags_entry.configure(state="normal")
            self.tags_entry.delete(0, "end")
            self.tags_entry.insert(0, self.selected_tags)
            self.tags_entry.configure(state="readonly")
            popup.destroy()
        
        def on_cancel():
            popup.destroy()
        
        ctk.CTkButton(button_frame, text="OK", command=on_ok).pack(side="right", padx=(10, 0))
        ctk.CTkButton(button_frame, text="Cancel", command=on_cancel).pack(side="right")
        
        # Focus on the popup
        popup.focus_set()

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

    def _on_save(self, *args):
        node_id = self.parent.metadata.start
        
        # Check if node exists in storymap, if not create a basic structure
        if node_id not in self.parent.story_map:
            # Create a new node with basic structure if it doesn't exist
            self.parent.story_map[node_id] = {
                "id": node_id,
                "description": "",
                "script": "",
                "choices": [],
                "metadata": {}
            }