import customtkinter as ctk
from typing import Union , Optional, Dict, Any, Literal, overload, cast , Callable
from typing import TypedDict , TypeVar
from cyoa_io import THEME
import os

# Define LayoutArgs as a type alias for a dictionary with string keys and any values
# Type alias for layout arguments
LayoutArgs = Dict[str, Any]

# Type aliases for configuration dictionaries
ContainerConfig = Dict[str, Any]
LabelConfig = Dict[str, Any]
ComponentConfig = Dict[str, Any]

# Type alias for component types
ComponentT = TypeVar('ComponentT', ctk.CTkEntry, ctk.CTkTextbox)

from dataclasses import dataclass

@dataclass(frozen=True)
class ThemeColors:
    """Immutable theme color definitions"""
    text_primary: str
    bg_secondary: str
    accent: str

class Utility:


    def create_input_component(
        self,
        parent: Union[ctk.CTkFrame, ctk.CTkScrollableFrame],
        label_text: str,
        default_value: str = "",
        component_type: Literal["entry", "text"] = "entry",
        layout: Literal["grid", "pack", "place"] = "grid",
        layout_args: Optional[LayoutArgs] = None,
        width: int = 200,
        height: Optional[int] = None,
        container_config: Optional[ContainerConfig] = None,
        label_config: Optional[LabelConfig] = None,
        component_config: Optional[ComponentConfig] = None
    ) -> Union[ctk.CTkEntry, ctk.CTkTextbox]:
        """
        Unified function to create labeled input components with maximum flexibility.
        
        Args:
            parent: Parent widget to contain this component
            label_text: Text to display in the label
            default_value: Initial value for the input component
            component_type: Type of input component ('entry' or 'text')
            layout: Layout manager to use ('grid', 'pack', or 'place')
            layout_args: Arguments to pass to the layout manager
            width: Width of the component in pixels
            height: Height of the component in pixels (only used for text areas)
            container_config: Configuration for the container frame
            label_config: Configuration for the label
            component_config: Configuration for the input component
            
        Returns:
            The created input component (CTkEntry or CTkTextbox)
            
        Raises:
            TypeError: If any parameter has an invalid type
            ValueError: If component_type or layout has an invalid value
        """
        # Type validation
        if not isinstance(parent, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
            raise TypeError(f"parent must be CTkFrame or CTkScrollableFrame, got {type(parent).__name__}")
        if not isinstance(label_text, str):
            raise TypeError(f"label_text must be str, got {type(label_text).__name__}")
        if not isinstance(default_value, str):
            raise TypeError(f"default_value must be str, got {type(default_value).__name__}")
        if component_type not in ("entry", "text"):
            raise ValueError(f"component_type must be 'entry' or 'text', got '{component_type}'")
        if layout not in ("grid", "pack", "place"):
            raise ValueError(f"layout must be 'grid', 'pack', or 'place', got '{layout}'")
        if not isinstance(width, int) or width <= 0:
            raise TypeError(f"width must be a positive integer, got {width}")
        if height is not None and (not isinstance(height, int) or height <= 0):
            raise TypeError(f"height must be None or a positive integer, got {height}")
        
        # Validate configuration dictionaries
        for config_name, config in [
            ("layout_args", layout_args),
            ("container_config", container_config),
            ("label_config", label_config),
            ("component_config", component_config)
        ]:
            if config is not None and not isinstance(config, dict):
                raise TypeError(f"{config_name} must be None or dict, got {type(config).__name__}")
        
        # Cache theme and font references to avoid repeated dictionary lookups
        if not hasattr(self, "_cached_theme"):
            # Validate THEME structure
            required_keys = ("text_primary", "bg_secondary", "accent")
            for key in required_keys:
                if key not in THEME:
                    raise KeyError(f"Required theme key '{key}' not found in THEME dictionary")
            
            self._cached_theme = ThemeColors(
                text_primary=THEME["text_primary"],
                bg_secondary=THEME["bg_secondary"],
                accent=THEME["accent"]
            )
        
        theme = self._cached_theme
        
        if not hasattr(self, "_cached_font"):
            if not hasattr(self, "default_font"):
                raise AttributeError("Class must have a 'default_font' attribute")
            self._cached_font = self.default_font # type: ignore
        
        default_font = self._cached_font
        
        # Set default configurations
        default_container_config: ContainerConfig = {"fg_color": "transparent"}
        default_label_config: LabelConfig = {
            "font": default_font,
            "text_color": theme.text_primary
        }
        default_component_config: ComponentConfig = {
            "font": default_font,
            "fg_color": theme.bg_secondary,
            "text_color": theme.text_primary,
            "border_color": theme.accent,
            "corner_radius": 8
        }
        
        # Apply user configurations with defaults
        container_config_merged: ContainerConfig = {**default_container_config, **(container_config or {})}
        label_config_merged: LabelConfig = {**default_label_config, **(label_config or {})}
        component_config_merged: ComponentConfig = {**default_component_config, **(component_config or {})}
        
        # Default layout arguments
        layout_args_merged: LayoutArgs
        if layout_args is None:
            layout_args_merged = {"padx": 10, "pady": 5} if layout == "grid" else {"fill": "x", "padx": 10, "pady": 5}
        else:
            layout_args_merged = layout_args
        
        # Create container frame
        container = ctk.CTkFrame(parent, **container_config_merged)
        
        # Apply layout manager
        if layout == "grid":
            container.grid(**layout_args_merged)
        elif layout == "pack":
            container.pack(**layout_args_merged)
        elif layout == "place":
            container.place(**layout_args_merged)
        
        # Create and configure label
        label = ctk.CTkLabel(container, text=label_text, **label_config_merged)
        
        # Create appropriate input component
        component: Union[ctk.CTkEntry, ctk.CTkTextbox]
        
        if component_type == "entry":
            # Add width to component config
            entry_config = component_config_merged.copy()
            entry_config["width"] = width
            
            # Create entry
            entry = ctk.CTkEntry(container, **entry_config)
            entry.insert(0, default_value)
            
            # Arrange components horizontally
            label.pack(side="left", padx=(0, 10))
            entry.pack(side="left", fill="x", expand=True)
            
            component = entry
            
        else:  # component_type == "text" (already validated above)
            # Add width and height to component config
            textbox_config = component_config_merged.copy()
            textbox_config["width"] = width
            textbox_config["height"] = height if height is not None else 100
            
            # Create text area
            textbox = ctk.CTkTextbox(container, **textbox_config)
            textbox.insert("0.0", default_value)
            
            # Arrange components vertically
            label.pack(side="top", anchor="w", pady=(0, 5))
            textbox.pack(fill="both", expand=True)
            
            component = textbox
        
        return component

    @overload
    def create_labeled_input(
        self,
        frame: Union[ctk.CTkFrame, ctk.CTkScrollableFrame],
        label_text: str,
        default_value: str = "",
        layout: Literal["grid"] = "grid",
        layout_options: Optional[Dict[str, Any]] = None,
        entry_width: int = 200,
        component_config: Optional[Dict[str, Any]] = None
    ) -> ctk.CTkEntry: ...

    @overload
    def create_labeled_input(
        self,
        frame: Union[ctk.CTkFrame, ctk.CTkScrollableFrame],
        label_text: str,
        default_value: str = "",
        layout: Literal["pack"] = "pack",
        layout_options: Optional[Dict[str, Any]] = None,
        entry_width: int = 200,
        component_config: Optional[Dict[str, Any]] = None
    ) -> ctk.CTkEntry: ...

    def create_labeled_input(
        self,
        frame: Union[ctk.CTkFrame, ctk.CTkScrollableFrame],
        label_text: str,
        default_value: str = "",
        layout: Literal["grid", "pack"] = "grid",
        layout_options: Optional[LayoutArgs] = None,
        entry_width: int = 200,
        component_config: Optional[ComponentConfig] = None
    ) -> ctk.CTkEntry:
        """
        Create a labeled entry with flexible layout (backward compatible).
        
        Args:
            frame: Parent frame for this component
            label_text: Text to display in the label
            default_value: Initial value for the entry
            layout: Layout manager to use ('grid' or 'pack')
            layout_options: Arguments to pass to the layout manager
            entry_width: Width of the entry field in pixels
            component_config: Additional configuration for the entry component
            
        Returns:
            The created CTkEntry component
            
        Raises:
            TypeError: If any parameter has an invalid type
            ValueError: If layout has an invalid value
        """
        # Type checking
        if not isinstance(frame, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
            raise TypeError(f"frame must be CTkFrame or CTkScrollableFrame, got {type(frame).__name__}")
        if not isinstance(label_text, str):
            raise TypeError(f"label_text must be str, got {type(label_text).__name__}")
        if not isinstance(default_value, str):
            raise TypeError(f"default_value must be str, got {type(default_value).__name__}")
        if layout not in ("grid", "pack"):
            raise ValueError(f"layout must be 'grid' or 'pack', got '{layout}'")
        if not isinstance(entry_width, int) or entry_width <= 0:
            raise TypeError(f"entry_width must be a positive integer, got {entry_width}")
        if layout_options is not None and not isinstance(layout_options, dict):
            raise TypeError(f"layout_options must be None or dict, got {type(layout_options).__name__}")
        if component_config is not None and not isinstance(component_config, dict):
            raise TypeError(f"component_config must be None or dict, got {type(component_config).__name__}")
        
        component = self.create_input_component(
            parent=frame,
            label_text=label_text,
            default_value=default_value,
            component_type="entry",
            layout=layout,
            layout_args=layout_options,
            width=entry_width,
            component_config=component_config
        )
        
        # Safe cast - we know it's an entry because we specified component_type="entry"
        return cast(ctk.CTkEntry, component)

    @overload
    def create_text_area(
        self,
        parent: Union[ctk.CTkFrame, ctk.CTkScrollableFrame],
        label_text: str,
        default_value: str = "",
        height: int = 5,
        use_pack: Literal[True] = True,
        row: int = 0,
        column: int = 0,
        columnspan: int = 2,
        sticky: str = "ew",
        component_config: Optional[Dict[str, Any]] = None
    ) -> ctk.CTkTextbox: ...

    @overload
    def create_text_area(
        self,
        parent: Union[ctk.CTkFrame, ctk.CTkScrollableFrame],
        label_text: str,
        default_value: str = "",
        height: int = 5,
        use_pack: Literal[False] = False,
        row: int = 0,
        column: int = 0,
        columnspan: int = 2,
        sticky: str = "ew",
        component_config: Optional[Dict[str, Any]] = None
    ) -> ctk.CTkTextbox: ...

    def create_text_area(
        self,
        parent: Union[ctk.CTkFrame, ctk.CTkScrollableFrame],
        label_text: str,
        default_value: str = "",
        height: int = 5,
        use_pack: bool = False,
        row: int = 0,
        column: int = 0,
        columnspan: int = 2,
        sticky: str = "ew",
        component_config: Optional[ComponentConfig] = None
    ) -> ctk.CTkTextbox:
        """
        Create a text area with label (backward compatible).
        
        Args:
            parent: Parent widget to contain this component
            label_text: Text to display in the label
            default_value: Initial value for the text area
            height: Height in number of text lines (multiplied by 20 for pixels)
            use_pack: If True, use pack layout manager; otherwise use grid
            row: Grid row position (only used if use_pack is False)
            column: Grid column position (only used if use_pack is False)
            columnspan: Grid column span (only used if use_pack is False)
            sticky: Grid sticky parameter (only used if use_pack is False)
            component_config: Additional configuration for the text component
            
        Returns:
            The created CTkTextbox component
            
        Raises:
            TypeError: If any parameter has an invalid type
        """
        # Type checking
        if not isinstance(parent, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
            raise TypeError(f"parent must be CTkFrame or CTkScrollableFrame, got {type(parent).__name__}")
        if not isinstance(label_text, str):
            raise TypeError(f"label_text must be str, got {type(label_text).__name__}")
        if not isinstance(default_value, str):
            raise TypeError(f"default_value must be str, got {type(default_value).__name__}")
        if not isinstance(height, int) or height <= 0:
            raise TypeError(f"height must be a positive integer, got {height}")
        if not isinstance(use_pack, bool):
            raise TypeError(f"use_pack must be bool, got {type(use_pack).__name__}")
        if not isinstance(row, int) or row < 0:
            raise TypeError(f"row must be a non-negative integer, got {row}")
        if not isinstance(column, int) or column < 0:
            raise TypeError(f"column must be a non-negative integer, got {column}")
        if not isinstance(columnspan, int) or columnspan <= 0:
            raise TypeError(f"columnspan must be a positive integer, got {columnspan}")
        if not isinstance(sticky, str):
            raise TypeError(f"sticky must be str, got {type(sticky).__name__}")
        if component_config is not None and not isinstance(component_config, dict):
            raise TypeError(f"component_config must be None or dict, got {type(component_config).__name__}")
        
        # Calculate pixel height
        pixel_height = height * 20  # Convert logical lines to pixels
        
        # Determine layout and layout arguments based on parameters
        layout: Literal["grid", "pack"] = "pack" if use_pack else "grid"
        
        layout_args: LayoutArgs
        if use_pack:
            layout_args = {"fill": "x", "padx": 10, "pady": 5}
        else:
            layout_args = {
                "row": row,
                "column": column,
                "columnspan": columnspan,
                "sticky": sticky,
                "padx": 10,
                "pady": 5
            }
        
        component = self.create_input_component(
            parent=parent,
            label_text=label_text,
            default_value=default_value,
            component_type="text",
            layout=layout,
            layout_args=layout_args,
            height=pixel_height,
            component_config=component_config
        )
        
        # Safe cast - we know it's a textbox because we specified component_type="text"
        return cast(ctk.CTkTextbox, component)
    
    def create_button_grid(self, parent: Union[ctk.CTkFrame, ctk.CTkScrollableFrame], text: str, command: Callable, 
                          width: Optional[int] = None, row: Optional[int] = None,
                          column: Optional[int] = None, **kwargs) -> ctk.CTkButton:
        button_kwargs = self._get_button_kwargs(text, command, width, **kwargs)
        button = ctk.CTkButton(parent,text_color=THEME["button_text"] , **button_kwargs)
        
        if row is not None and column is not None:
            button.grid(row=row, column=column, padx=5, pady=5)
        return button
    def _get_button_kwargs(self, text: str, command: Callable, 
                          width: Optional[int], **kwargs) -> Dict[str, Any]:
        button_kwargs = {
            "text": text,
            "command": command,
            "font": self.default_font, # type: ignore
            "width": width,
            "corner_radius": 8
        }
        
        if "fg_color" not in kwargs:
            button_kwargs["fg_color"] = THEME["accent"]
        if "hover_color" not in kwargs:
            button_kwargs["hover_color"] = THEME["button_hover"]
            
        button_kwargs.update(kwargs)
        return button_kwargs
    
    def create_story_file(self,name: str, filename: str, content: str) -> str:
        base_folder = "story"
        subfolder = os.path.join(base_folder, name)
        
        # Create the base and subfolder if they don't exist
        os.makedirs(subfolder, exist_ok=True)
        
        file_path = os.path.join(subfolder, filename)
        
        # Write content to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
import customtkinter as ctk
import tkinter as tk

class ScrollableComboBox(ctk.CTkFrame):
    def __init__(self, master, values, command=None, default=None, max_visible=8, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.values = values
        self.max_visible = max_visible
        self.dropdown = None
        self._filtered_values = values
        self._is_typing = False
        
        # Create entry widget
        self.entry = ctk.CTkEntry(self)
        self.entry.pack(fill="x")
        
        # Bind events
        self.entry.bind("<Button-1>", self._on_entry_click)
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<Up>", self._on_arrow_key)
        self.entry.bind("<Down>", self._on_arrow_key)
        
        if default:
            self.set(default)

    def _on_entry_click(self, event):
        """Handle entry click to show/hide dropdown"""
        if self.dropdown and self.dropdown.winfo_exists():
            self._hide_dropdown()
        else:
            self._show_dropdown()

    def _on_key_release(self, event):
        """Handle typing in entry for filtering"""
        if event.keysym in ['Up', 'Down', 'Return', 'Tab', 'Escape']:
            return
            
        self._is_typing = True
        search_text = self.entry.get().lower()
        
        # Filter values based on search
        if not search_text:
            self._filtered_values = self.values
        else:
            self._filtered_values = [v for v in self.values if search_text in v.lower()]
        
        # Show dropdown if not visible and there are filtered results
        if not (self.dropdown and self.dropdown.winfo_exists()):
            self._show_dropdown()
        else:
            self._update_dropdown_buttons()
        
        # Stop typing flag after a delay
        self.after(100, lambda: setattr(self, '_is_typing', False))

    def _on_arrow_key(self, event):
        """Handle arrow key navigation"""
        if not (self.dropdown and self.dropdown.winfo_exists()):
            self._show_dropdown()

    def _show_dropdown(self):
        """Create and show the dropdown"""
        if self.dropdown and self.dropdown.winfo_exists():
            return
            
        # Calculate dropdown dimensions
        visible_items = min(len(self._filtered_values), self.max_visible)
        if visible_items == 0:
            visible_items = 1  # For "No results" message
        
        item_height = 32
        dropdown_height = visible_items * item_height + 20
        dropdown_width = max(200, self.winfo_width())
        
        # Calculate position
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 2
        
        # Adjust if dropdown goes off screen
        screen_height = self.winfo_screenheight()
        if y + dropdown_height > screen_height - 50:
            y = self.winfo_rooty() - dropdown_height - 2
        
        # Create dropdown window
        self.dropdown = ctk.CTkToplevel(self)
        self.dropdown.geometry(f"{dropdown_width}x{dropdown_height}+{x}+{y}")
        self.dropdown.overrideredirect(True)
        self.dropdown.attributes('-topmost', True)
        
        # Prevent dropdown from taking focus away from entry
        self.dropdown.focus_set = lambda: None
        
        # Create scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.dropdown, 
            width=dropdown_width-20, 
            height=dropdown_height-20
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add buttons
        self._update_dropdown_buttons()
        
        # Set up cleanup timer
        self._schedule_cleanup()

    def _update_dropdown_buttons(self):
        """Update the dropdown button list"""
        # Clear existing buttons
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        if not self._filtered_values:
            # Show "no results" message
            no_results = ctk.CTkLabel(
                self.scroll_frame, 
                text="No matches found",
                text_color=("gray60", "gray40")
            )
            no_results.pack(pady=10)
            return
        
        # Create buttons for filtered values
        for value in self._filtered_values:
            btn = ctk.CTkButton(
                self.scroll_frame,
                text=value,
                height=28,
                anchor="w",
                command=lambda v=value: self._select_value(v),
                hover_color=("gray80", "gray20")
            )
            btn.pack(fill="x", padx=2, pady=1)

    def _select_value(self, value):
        """Select a value from dropdown"""
        self.set(value)
        self._hide_dropdown()
        
        # Call command callback
        if self.command:
            try:
                self.command(value)
            except Exception as e:
                print(f"Error in command callback: {e}")

    def _hide_dropdown(self):
        """Hide the dropdown"""
        if self.dropdown and self.dropdown.winfo_exists():
            self.dropdown.destroy()
        self.dropdown = None

    def _schedule_cleanup(self):
        """Schedule cleanup check for dropdown"""
        def check_cleanup():
            if not (self.dropdown and self.dropdown.winfo_exists()):
                return
            
            # Don't close if user is actively typing
            if self._is_typing:
                self.after(200, check_cleanup)
                return
            
            try:
                # Check if mouse is over dropdown or entry
                mouse_x = self.winfo_pointerx()
                mouse_y = self.winfo_pointery()
                
                # Get dropdown bounds
                dropdown_x1 = self.dropdown.winfo_rootx()
                dropdown_y1 = self.dropdown.winfo_rooty()
                dropdown_x2 = dropdown_x1 + self.dropdown.winfo_width()
                dropdown_y2 = dropdown_y1 + self.dropdown.winfo_height()
                
                # Get entry bounds
                entry_x1 = self.entry.winfo_rootx()
                entry_y1 = self.entry.winfo_rooty()
                entry_x2 = entry_x1 + self.entry.winfo_width()
                entry_y2 = entry_y1 + self.entry.winfo_height()
                
                # Check if mouse is over dropdown or entry
                mouse_over_dropdown = (dropdown_x1 <= mouse_x <= dropdown_x2 and 
                                     dropdown_y1 <= mouse_y <= dropdown_y2)
                mouse_over_entry = (entry_x1 <= mouse_x <= entry_x2 and 
                                  entry_y1 <= mouse_y <= entry_y2)
                
                # Close if mouse is not over either
                if not (mouse_over_dropdown or mouse_over_entry):
                    # Check if entry has focus
                    if self.entry.focus_get() != self.entry:
                        self._hide_dropdown()
                        return
                
                # Continue checking
                self.after(200, check_cleanup)
                
            except tk.TclError:
                # Widget was destroyed
                pass
        
        # Start cleanup check after a delay
        self.after(500, check_cleanup)

    def get(self):
        """Get the current value"""
        return self.entry.get()

    def set(self, value):
        """Set the current value"""
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))

    def destroy(self):
        """Clean up when widget is destroyed"""
        self._hide_dropdown()
        super().destroy()

# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("400x300")
    
    # Test with many values
    values = [f"Option {i}" for i in range(100)]
    
    def on_select(value):
        print(f"Selected: {value}")
    
    combo = ScrollableComboBox(
        root, 
        values=values, 
        command=on_select,
        default="Option 1"
    )
    combo.pack(padx=20, pady=20, fill="x")
    
    root.mainloop()