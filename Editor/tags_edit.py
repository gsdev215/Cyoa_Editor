import customtkinter as ctk
from typing import List, Callable, Optional
import re

class SmartDropdown(ctk.CTkFrame):
    def __init__(self, master, values: List[str], 
                 placeholder: str = "Type to search...",
                 max_results: int = 8,
                 allow_duplicates: bool = False,
                 case_sensitive: bool = False,
                 on_selection_change: Optional[Callable] = None,
                 **kwargs):
        super().__init__(master, **kwargs)
        
        # Configuration
        self.values = sorted(set(values))  # Remove duplicates and sort
        self.original_values = values.copy()
        self.selected = []
        self.max_results = max_results
        self.allow_duplicates = allow_duplicates
        self.case_sensitive = case_sensitive
        self.on_selection_change = on_selection_change
        
        # State tracking
        self.dropdown_visible = False
        self.current_focus_index = -1
        
        self._setup_ui(placeholder)
        self._setup_bindings()
    
    def _setup_ui(self, placeholder: str):
        """Initialize the UI components"""
        # Search input with placeholder
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        self.input = ctk.CTkEntry(self.input_frame, placeholder_text=placeholder)
        self.input.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Clear button
        self.clear_btn = ctk.CTkButton(
            self.input_frame, text="✕", width=30, height=30,
            command=self.clear_input,
            fg_color="transparent",
            hover_color=("gray75", "gray25")
        )
        self.clear_btn.pack(side="right")
        
        # Selected items display with controls
        self.selected_frame = ctk.CTkFrame(self)
        self.selected_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header for selected items
        header_frame = ctk.CTkFrame(self.selected_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        self.selected_label = ctk.CTkLabel(
            header_frame, text="Selected Items (0)", 
            font=ctk.CTkFont(weight="bold")
        )
        self.selected_label.pack(side="left")
        
        # Control buttons
        self.clear_all_btn = ctk.CTkButton(
            header_frame, text="Clear All", width=80, height=25,
            command=self.clear_all_selected,
            fg_color="transparent",
            border_width=1
        )
        self.clear_all_btn.pack(side="right", padx=(5, 0))
        
        # Selected items textbox
        self.selected_box = ctk.CTkTextbox(self.selected_frame, height=120)
        self.selected_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.selected_box.configure(state="disabled")  # Read-only
        
        # Dropdown container
        self.dropdown = ctk.CTkScrollableFrame(self, height=0)
        self.dropdown.pack(fill="x", padx=5)
        self.dropdown_widgets = []
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self, text="", 
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray50")
        )
        self.status_label.pack(pady=(0, 5))
    
    def _setup_bindings(self):
        """Setup event bindings"""
        self.input.bind("<KeyRelease>", self._on_key_release)
        self.input.bind("<Key>", self._on_key_press)
        self.input.bind("<FocusIn>", self._on_focus_in)
        self.input.bind("<FocusOut>", self._on_focus_out)
    
    def _on_key_release(self, event):
        """Handle key release events"""
        if event.keysym in ["Up", "Down", "Return", "Escape"]:
            return
        self.update_dropdown()
    
    def _on_key_press(self, event):
        """Handle special key presses"""
        if not self.dropdown_visible:
            return
            
        if event.keysym == "Down":
            self._navigate_dropdown(1)
            return "break"
        elif event.keysym == "Up":
            self._navigate_dropdown(-1)
            return "break"
        elif event.keysym == "Return":
            self._select_focused_item()
            return "break"
        elif event.keysym == "Escape":
            self.hide_dropdown()
            return "break"
    
    def _on_focus_in(self, event):
        """Handle input focus"""
        if self.input.get().strip():
            self.update_dropdown()
    
    def _on_focus_out(self, event):
        """Handle input focus loss - hide dropdown after small delay"""
        self.after(150, self._check_hide_dropdown)
    
    def _check_hide_dropdown(self):
        """Check if dropdown should be hidden after focus loss"""
        # Check if focus is still within our widget hierarchy
        focused_widget = self.focus_get()
        if not focused_widget or not self._is_widget_inside(focused_widget):
            self.hide_dropdown()
    
    def _is_widget_inside(self, widget) -> bool:
        """Check if widget is inside this dropdown component"""
        current = widget
        while current:
            if current == self:
                return True
            try:
                current = current.master
            except AttributeError:
                break
        return False
    
    def select_value(self, value: str):
        """Select a value and add it to selected items"""
        if not self.allow_duplicates and value in self.selected:
            return
        
        self.selected.append(value)
        self._update_selected_display()
        
        # Clear input and hide dropdown
        self.clear_input()
        
        # Trigger callback if provided
        if self.on_selection_change:
            self.on_selection_change(self.selected.copy())
    
    def remove_selected(self, value: str):
        """Remove a value from selected items"""
        if value in self.selected:
            self.selected.remove(value)
            self._update_selected_display()
            
            if self.on_selection_change:
                self.on_selection_change(self.selected.copy())
    
    def clear_input(self):
        """Clear the search input"""
        self.input.delete(0, "end")
        self.hide_dropdown()
    
    def clear_all_selected(self):
        """Clear all selected items"""
        if self.selected:
            self.selected.clear()
            self._update_selected_display()
            
            if self.on_selection_change:
                self.on_selection_change(self.selected.copy())
    
    def _update_selected_display(self):
        """Update the selected items display"""
        self.selected_box.configure(state="normal")
        self.selected_box.delete("1.0", "end")
        
        if self.selected:
            for i, item in enumerate(self.selected, 1):
                self.selected_box.insert("end", f"{i}. {item}\n")
        else:
            self.selected_box.insert("end", "No items selected")
        
        self.selected_box.configure(state="disabled")
        
        # Update label
        count = len(self.selected)
        self.selected_label.configure(text=f"Selected Items ({count})")
    
    def _update_status(self, message: str):
        """Update status message"""
        self.status_label.configure(text=message)
    
    # Public API methods
    def get_selected(self) -> List[str]:
        """Get list of selected values"""
        return self.selected.copy()
    
    def set_selected(self, values: List[str]):
        """Set selected values"""
        self.selected = [v for v in values if v in self.values]
        self._update_selected_display()
    
    def add_values(self, new_values: List[str]):
        """Add new values to the dropdown"""
        self.values.extend(new_values)
        self.values = sorted(set(self.values))
    
    def set_values(self, values: List[str]):
        """Replace all values"""
        self.values = sorted(set(values))
        self.selected = [v for v in self.selected if v in self.values]
        self._update_selected_display()

    def _navigate_dropdown(self, direction: int):
        """Navigate dropdown with arrow keys"""
        if not self.dropdown_widgets:
            return
            
        # Update focus index
        self.current_focus_index += direction
        self.current_focus_index = max(0, min(len(self.dropdown_widgets) - 1, 
                                            self.current_focus_index))
        
        # Update button appearances
        for i, btn in enumerate(self.dropdown_widgets):
            if i == self.current_focus_index:
                btn.configure(fg_color=("gray70", "gray30"))
            else:
                btn.configure(fg_color=["gray84", "gray25"])
    
    def _select_focused_item(self):
        """Select the currently focused item"""
        if (0 <= self.current_focus_index < len(self.dropdown_widgets)):
            # Get the command from the button and execute it
            btn = self.dropdown_widgets[self.current_focus_index]
            btn.invoke()
    
    def update_dropdown(self):
        """Update dropdown based on current input"""
        query = self.input.get().strip()
        
        if not query:
            self.hide_dropdown()
            return
        
        # Clear previous dropdown
        self._clear_dropdown()
        
        # Find matches
        matches = self._find_matches(query)
        
        if matches:
            self._show_matches(matches)
            self.show_dropdown()
            self._update_status(f"Found {len(matches)} matches")
        else:
            self.hide_dropdown()
            self._update_status("No matches found")
    
    def _find_matches(self, query: str) -> List[str]:
        """Find matching values based on query"""
        if not self.case_sensitive:
            query = query.lower()
        
        matches = []
        query_pattern = re.escape(query)
        
        for value in self.values:
            search_value = value if self.case_sensitive else value.lower()
            
            # Skip if already selected (unless duplicates allowed)
            if not self.allow_duplicates and value in self.selected:
                continue
            
            # Check for matches (starts with, then contains)
            if search_value.startswith(query):
                matches.append(value)
            elif re.search(query_pattern, search_value):
                matches.append(value)
        
        return matches[:self.max_results]
    
    def _show_matches(self, matches: List[str]):
        """Display matching options in dropdown"""
        self.current_focus_index = -1
        
        for match in matches:
            btn = ctk.CTkButton(
                self.dropdown, text=match, height=32,
                command=lambda m=match: self.select_value(m),
                fg_color=("gray84", "gray25"),
                hover_color=("gray70", "gray30"),
                anchor="w"
            )
            btn.pack(fill="x", padx=2, pady=1)
            self.dropdown_widgets.append(btn)
    
    def _clear_dropdown(self):
        """Clear all dropdown widgets"""
        for widget in self.dropdown_widgets:
            widget.destroy()
        self.dropdown_widgets.clear()
    
    def show_dropdown(self):
        """Show the dropdown"""
        if not self.dropdown_visible:
            self.dropdown.configure(height=min(200, len(self.dropdown_widgets) * 35))
            self.dropdown_visible = True
    
    def hide_dropdown(self):
        """Hide the dropdown"""
        if self.dropdown_visible:
            self.dropdown.configure(height=0)
            self.dropdown_visible = False
            self._clear_dropdown()
            self._update_status("")


# Demo application
if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.geometry("500x600")
    app.title("Enhanced Smart Dropdown Demo")

    # Sample data
    sample_values = [
        "apple", "application", "apply", "approach", "appropriate",
        "banana", "band", "bank", "bar", "base", "basic", "battle",
        "beautiful", "become", "begin", "behavior", "believe", "benefit",
        "big", "binary", "bind", "bike", "bit", "bucket", "bus", "business",
        "call", "camera", "can", "car", "card", "care", "carry", "case",
        "category", "cause", "center", "central", "certain", "chair", "challenge",
        "change", "character", "charge", "check", "choice", "choose", "city",
        "clear", "close", "code", "cold", "collection", "color", "come",
        "commercial", "common", "community", "company", "compare", "complete"
    ]

    def on_selection_changed(selected_items):
        print(f"Selection changed: {selected_items}")

    # Create dropdown with enhanced features
    dropdown = SmartDropdown(
        app, 
        values=sample_values,
        placeholder="Search items...",
        max_results=10,
        allow_duplicates=False,
        case_sensitive=False,
        on_selection_change=on_selection_changed
    )
    dropdown.pack(padx=20, pady=20, fill="both", expand=True)

    # Add some example buttons
    button_frame = ctk.CTkFrame(app, fg_color="transparent")
    button_frame.pack(fill="x", padx=20, pady=(0, 20))

    def show_selected():
        selected = dropdown.get_selected()
        print(f"Currently selected: {selected}")

    def preset_selection():
        dropdown.set_selected(["apple", "banana", "car"])

    ctk.CTkButton(button_frame, text="Show Selected", 
                  command=show_selected).pack(side="left", padx=(0, 10))
    ctk.CTkButton(button_frame, text="Preset Selection", 
                  command=preset_selection).pack(side="left")

    app.mainloop()