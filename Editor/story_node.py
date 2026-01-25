import customtkinter as ctk
from typing import TYPE_CHECKING, Union, List, Dict, Any, Optional
from uuid import uuid4
import json

from cyoa_io import THEME
from Editor.utility import Utility , ScrollableComboBox

if TYPE_CHECKING:
    from TkApp import CYOAMakerApplication as CYOAMaker

Choice = Dict[str, Any]

class StoryNode(Utility):
    def __init__(self, parent: 'CYOAMaker'):
        self.parent = parent
        self.root = parent.root
        self.default_font = parent.default_font

    def to_lua_table(self, data):
        """Converts a Python dict/list to a Lua table string."""
        if isinstance(data, list):
            items = [self.to_lua_table(item) for item in data]
            return "{" + ", ".join(items) + "}"
        elif isinstance(data, dict):
            items = [f'["{k}"] = {self.to_lua_table(v)}' if not k.replace("-","").isalnum() 
                    else f'{k} = {self.to_lua_table(v)}' for k, v in data.items()]
            return "{" + ", ".join(items) + "}"
        elif isinstance(data, str):
            # Escape backslashes and double brackets just in case
            safe_str = data.replace('\\', '\\\\').replace(']]', r']\ ]')
            return f'[[{safe_str}]]'
        elif isinstance(data, bool):
            return "true" if data else "false"
        else:
            return str(data)

    def build_frame(self, node_id: str) -> ctk.CTkFrame:
        # Use .get with defaults to safely access keys

        # Create or get the node in the storymap
        node = self.parent.story_map.setdefault(node_id, {
            "id": node_id,
            "choices": [],
            "description": "",
            "url": "",
            "script": ""
        })

        current = node
        url = current.get("url", "")
        description = current.get("description", "")
        choices = current.get("choices", [])

        # Generate script
        scr = f'url = "{url}"\n'
        # Using [[ ]] for description is great for multi-line text
        scr += f'description = [[{description}]]\n\n'
        scr += "-- choice_{choice_id} = true <- true: enabled; false: disabled\n"

        for choice in choices:
            choice_id = choice.get('id', 'unknown')
            # Lua variables cannot have hyphens, so underscores are the way to go
            lua_safe_id = choice_id.replace('-', '_')
            scr += f"choice_{lua_safe_id} = true\n"

        # Use the helper instead of json.dumps
        scr += f"\nchoices = {self.to_lua_table(choices)}\n\n"
        scr += "-- The values above will auto update after saving --\n"

        node["script"] = scr

        # Ensure fields exist in the node dictionary
        node.setdefault("choices", [])
        node.setdefault("description", "")
        node.setdefault("url", "")
        node.setdefault("script", scr)
        node.setdefault("ending", "None")

        # Update the current node
        self.parent.current_node_data = node

        # Build the UI
        frame = self._create_main_frame()
        scrollable_frame = self._create_scrollable_area(frame)
        self._bind_scroll_events(scrollable_frame)

        self._build_node_fields(scrollable_frame, node)
        self._build_choices_section(scrollable_frame, node)
        self._build_button_bar(scrollable_frame, node)

        return frame

    def _create_main_frame(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.root, fg_color=THEME["bg_primary"])
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text="Story Node Editor",
            font=("Segoe UI", 24, "bold"),
            text_color=THEME["accent"]
        ).grid(row=0, column=0, pady=(10, 20), sticky="n")

        return frame

    def _create_scrollable_area(self, parent: ctk.CTkFrame) -> ctk.CTkScrollableFrame:
        scroll = ctk.CTkScrollableFrame(parent, fg_color=THEME["bg_primary"], width=700, height=600, corner_radius=12)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        return scroll

    def _bind_scroll_events(self, scrollable_frame):
        def _on_mousewheel(event):
            delta = event.delta if hasattr(event, 'delta') else (120 if event.num == 4 else -120)
            scrollable_frame._parent_canvas.yview_scroll(-int(delta / 120), "units")
            return "break"

        scrollable_frame.bind("<Enter>", lambda e: scrollable_frame._parent_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        scrollable_frame.bind("<Leave>", lambda e: scrollable_frame._parent_canvas.unbind_all("<MouseWheel>"))
        scrollable_frame.bind("<Destroy>", lambda e: scrollable_frame._parent_canvas.unbind_all("<MouseWheel>"))

    def _build_node_fields(self, frame, node):
        self.node_id = self.create_labeled_input(
            frame,
            label_text="Node ID",
            default_value=node["id"],
            layout="grid",
            layout_options={"row": 0, "column": 0, "sticky": "ew", "padx": 10, "pady": 5}
        )
        self.node_id.configure(state="readonly")

        self.description = self.create_text_area(frame, "Description", default_value=node["description"], use_pack=False, row=1, height=10)
        self.url = self.create_text_area(frame, "URL", default_value=node["url"], use_pack=False, row=2, height=1)
        self.script = self.create_text_area(frame, "Script", default_value=node["script"], use_pack=False, row=3, height=6)
        self.ending = ScrollableComboBox(frame, values=list(self.parent.endings.keys()), default=node["ending"], width=300, height=30, corner_radius=12, fg_color=THEME["bg_secondary"]) 
        self.ending.grid(row=4, column=0, sticky='ew', padx=10, pady=5)

    def _build_choices_section(self, frame, node):
        ctk.CTkLabel(
            frame,
            text="Choices",
            font=("Segoe UI", 16, "bold"),
            text_color=THEME["accent"]
        ).grid(row=5, column=0, pady=(20, 10), sticky='w', padx=10)

        self.choices = ctk.CTkFrame(frame, fg_color=THEME["bg_secondary"], corner_radius=12, height=1)
        self.choices.grid(row=6, column=0, sticky='ew', padx=10, pady=5)
        self.choices.grid_columnconfigure(0, weight=1)

        for choice in node["choices"]:
            self.add_existing_choice(self.choices, choice)

    def _build_button_bar(self, frame, node):
        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.grid(row=7, column=0, pady=20)
        container.grid_columnconfigure((0, 1), weight=1)

        self.create_button_grid(
            container, "Add Choice",
            command=lambda: self.add_new_choice(self.root),
            width=150, row=0, column=0
        )
        self.create_button_grid(
            container, "Save",
            command=lambda: self.save_options(self.root, self.description, self.url, self.script, self.ending),
            width=150, row=0, column=1
        )

    def add_existing_choice(self, parent, choice: dict):
        node = self.parent.current_node_data
        row_index = len(self.choices.winfo_children())

        container = ctk.CTkFrame(self.choices, fg_color=THEME["choice_bg"], corner_radius=8)
        container.grid(row=row_index, column=0, sticky="ew", padx=10, pady=5)

        emoji_entry = self._readonly_entry(container, choice["emoji"], width=40)
        id_entry = self._readonly_entry(container, choice["id"], width=400)
        emoji_entry.grid(row=0, column=0, padx=10, pady=5)
        id_entry.grid(row=0, column=1, padx=10, pady=5)

        self.create_button_grid(
            container, "...",
            command=lambda: self._open_choice_details(parent, choice),
            width=30, row=0, column=2
        )
        self.create_button_grid(
            container, "X",
            command=lambda: self.remove_choice(node, choice),
            width=30, row=0, column=3,
            fg_color="#900000"
        )

    def _readonly_entry(self, parent, value: str, width: int):
        entry = ctk.CTkEntry(
            parent,
            font=self.default_font,
            width=width,
            fg_color=THEME["bg_secondary"],
            text_color=THEME["text_primary"],
            border_color=THEME["accent"],
            corner_radius=8
        )
        entry.insert(0, value)
        entry.configure(state="readonly")
        return entry

    def _open_choice_details(self, parent, choice):
        self.save_options(self.root, self.description, self.url, self.script, self.ending)
        print("Opening choice editor")
        self.parent.show_choice_editor(
            parent,
            choice,
            self.parent.current_node_data,
            save_callback=self.refresh_choices # type: ignore
        )

    def add_new_choice(self, parent, new_choice: Optional[Choice] = None):
        node = self.parent.current_node_data
        if not new_choice:
            existing_ids = {c["id"] for c in node["choices"]}
            new_id = str(uuid4())
            while new_id in existing_ids:
                new_id = str(uuid4())
            new_choice = {"emoji": "", "id": new_id, "text": "", "script": "", "parent": node["id"]}

        index = self._find_choice_index(node["choices"], new_choice["id"])
        if index is not None:
            node["choices"][index] = new_choice
        else:
            node["choices"].append(new_choice)

        self.refresh_choices()

    def remove_choice(self, node: dict, choice: dict):
        node["choices"].remove(choice)
        self.refresh_choices()

    def refresh_choices(self):
        for widget in self.choices.winfo_children():
            widget.destroy()
        for choice in self.parent.current_node_data["choices"]:
            self.add_existing_choice(self.choices, choice)

    def save_options(self, window, desc_entry, url_entry, script_entry, ending):
        node = self.parent.current_node_data
        node.update({
            "description": desc_entry.get("0.0", "end").strip().replace('"', '“').replace("'", "′"),
            "url": url_entry.get("0.0", "end").strip(),
            "script": script_entry.get("0.0", "end").strip(),
            "ending": ending.get().strip()
        })
        self.parent.story_map[node["id"]] = node
        print(script_entry.get("0.0", "end").strip())
        self.parent._show_story_node_editor(node["id"])

    def _find_choice_index(self, choices: List[Choice], choice_id: str) -> Optional[int]:
        return next((i for i, c in enumerate(choices) if c["id"] == choice_id), None)
