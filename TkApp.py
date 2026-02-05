# -*- coding: utf-8 -*-
"""
CYOA (Choose Your Own Adventure) Maker - Main Application
Provides a GUI editor for creating interactive story adventures.
"""

# GUI imports
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk

# Local module imports
from Editor.story_node import StoryNode
from Editor.choice import Choice
from Editor.emoji_editor import EmojiEditor
from Editor.main_menu import MainMenu
from cyoa_io import Metadata, load_cyoa_file, save_cyoa_file, PREDEFINED_TAGS, UI_THEME , ENDINGS
from emojiSchema import EmojiSchema

# Standard libraries
from uuid import uuid4
import json
import pickle
import os
import threading
import time
import asyncio
from typing import Dict, Any, Optional


class CYOAMakerApplication:
    """Main application class for the CYOA Maker GUI editor."""
    
    def __init__(self, root: ctk.CTk):
        """Initialize the CYOA Maker application."""
        self.root = root
        self._setup_window()
        
        # UI state
        self.current_view = None
        
        # Core data structures
        self.player_data = {"StartID": str(uuid4())}
        self.player_data['currentID'] = self.player_data['StartID']
        self.story_map = {}
        self.metadata: Metadata = Metadata("", "", str(uuid4()), "", "", [""], "")
        self.current_node_data = {}
        self.emoji_schema = EmojiSchema()
        self.endings = ENDINGS
        
        # Configuration
        self.default_font = ("Noto Sans", 12)
        self.shared_data_filepath = "cyoa_shared_data.pkl"
        
        # Background processing
        self._is_save_thread_running = True
        self._background_save_thread = threading.Thread(
            target=self._run_periodic_background_tasks, 
            daemon=True
        )
        self._background_save_thread.start()
        
        self._show_main_menu()
    
    def _setup_window(self):
        """Configure the main window appearance and layout."""
        self.root.configure(fg_color=UI_THEME["bg_primary"])
        self.root.grid_rowconfigure(0, weight=1, minsize=100)
        self.root.grid_columnconfigure(0, weight=1, minsize=100)
    
    def _run_periodic_background_tasks(self):
        """Execute background tasks in a separate thread with async support."""
        async def async_task_loop():
            while self._is_save_thread_running:
                try:
                    # print(f"Current story map: {self.story_map}")
                    await self._save_shared_data_async()
                    await self._check_for_external_commands_async()
                except Exception as error:
                    print(f"[Background Task] Error: {error}")
                await asyncio.sleep(0.5)
        
        asyncio.run(async_task_loop())
    
    async def _check_for_external_commands_async(self):
        """Check for external commands from other processes (async version)."""
        await self._save_shared_data_async()
        
        command_file_path = "cyoa_commands.pkl"
        if not os.path.exists(command_file_path):
            return
        
        try:
            # Load and process command
            loop = asyncio.get_running_loop()
            with open(command_file_path, 'rb') as file:
                command_data = await loop.run_in_executor(None, pickle.load, file)
            
            command = command_data.get("command")
            
            if command == "edit_node":
                node_id = command_data.get("node_id")
                if node_id:
                    self._ensure_node_exists(node_id)
                    self.root.after(0, lambda: self._show_story_node_editor(node_id))
            
            elif command == "Save":
                if self.story_map:
                    self._save_project_with_dialog()
                self.root.quit()
            
            # Clean up command file
            os.remove(command_file_path)
            
        except Exception as error:
            print(f"Error processing external commands: {error}")
            self._cleanup_command_file(command_file_path)
    
    def _cleanup_command_file(self, filepath: str):
        """Safely remove command file if it exists."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
    
    def _ensure_node_exists(self, node_id: str):
        """Ensure a story node exists in the story map."""
        if node_id not in self.story_map:
            print(f"Node {node_id} not found, creating new node")
    
    def _save_project_with_dialog(self):
        """Save the current project using a file dialog."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".cyoa", 
            filetypes=[("CYOA Files", "*.cy")]
        )
        if filename:
            try:
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                save_cyoa_file(
                    filename=filename, 
                    metadata=self.metadata, 
                    player_data=self.player_data, 
                    story_map=self.story_map,
                    emoji_schema=self.emoji_schema.get_json_schema()
                )
                messagebox.showinfo("Save", "Project saved successfully!")
            except Exception as error:
                messagebox.showerror("Error", f"Failed to save project: {error}")
    
    async def _save_shared_data_async(self):
        """Save current application state to shared data file (async version)."""
        try:
            shared_data = {
                "storymap": self.story_map,
                "playerdata": self.player_data,
                "metadata": {
                    "title": getattr(self.metadata, 'title', ''),
                    "author": getattr(self.metadata, 'author', ''),
                    "version": getattr(self.metadata, 'version', ''),
                    "description": getattr(self.metadata, 'description', ''),
                } if self.metadata else {}
            }
            
            loop = asyncio.get_running_loop()
            with open(self.shared_data_filepath, 'wb') as file:
                await loop.run_in_executor(None, pickle.dump, shared_data, file)
                
        except Exception as error:
            print(f"Error saving shared data: {error}")
    
    def save_shared_data(self):
        """Thread-safe wrapper for saving shared data."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self._save_shared_data_async())
            else:
                loop.run_until_complete(self._save_shared_data_async())
        except RuntimeError:
            # No running event loop, create new one
            asyncio.run(self._save_shared_data_async())
        except Exception as error:
            print(f"Error in save wrapper: {error}")
    
    def load_shared_data(self) -> Optional[Dict[str, Any]]:
        """Load application state from shared data file."""
        try:
            if os.path.exists(self.shared_data_filepath):
                with open(self.shared_data_filepath, 'rb') as file:
                    return pickle.load(file)
        except Exception as error:
            print(f"Error loading shared data: {error}")
        return None
    
    def _clear_current_view(self):
        """Clear the currently displayed view."""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
    
    def _show_main_menu(self):
        """Display the main menu interface."""
        self._clear_current_view()
        
        frame = ctk.CTkFrame(self.root, fg_color=UI_THEME["bg_primary"])
        frame.pack(fill="both", expand=True)
        
        menu_buttons = [
            ("New Project", self._show_project_menu),
            ("Emoji Schema", self._show_emoji_editor),
            ("Load Project", self._load_project_from_dialog),
            ("Exit", self.root.destroy)
        ]
        
        for button_text, command in menu_buttons:
            ctk.CTkButton(
                frame,
                text=button_text,
                command=command,
                fg_color=UI_THEME["accent"],
                font=self.default_font,
                text_color=UI_THEME["button_text"]
            ).pack(pady=20)
        
        self.current_view = frame
    
    def _show_story_node_editor(self, node_id: Optional[str] = None):
        """Display the story node editor interface."""
        self._clear_current_view()
        
        # Determine which node to edit
        target_node_id = node_id or self.player_data["StartID"]
        
        # Ensure node exists with basic structure
        if target_node_id not in self.story_map:
            self.story_map[target_node_id] = {
                "id": target_node_id,
                "description": "",
                "script": "",
                "choices": [],
                "metadata": {}
            }
        
        # Ensure node has required 'id' field
        if "id" not in self.story_map[target_node_id]:
            self.story_map[target_node_id]["id"] = target_node_id
        
        # Reset current node data if switching nodes
        if node_id and node_id != self.current_node_data.get("id"):
            self.current_node_data = {}
        
        try:
            self.current_view = StoryNode(self).build_frame(node_id=target_node_id)
            self.save_shared_data()
        except Exception as error:
            print(f"Error building story node editor: {error}")
            # Fallback to main menu on error
            self._show_main_menu()
    
    def show_choice_editor(self, parent_window, choice_data, node_data, save_callback=None):
        """Display the choice editor interface."""
        self._clear_current_view()
        self.current_view = Choice(self).build_frame(
            parent_window, choice_data, node_data, save_callback
        )
    
    def _show_emoji_editor(self):
        """Display the emoji editor interface."""
        self._clear_current_view()
        self.current_view = EmojiEditor(self).build_frame()
    
    def _show_project_menu(self):
        """Display the project management menu."""
        self._clear_current_view()
        self.current_view = MainMenu(self).build_frame()
    
    def update_story_map(self, node_id: str, node_data: Dict[str, Any]):
        """Update story map with new node data and save."""
        self.story_map[node_id] = node_data
        self.save_shared_data()
    
    def remove_story_node(self, node_id: str):
        """Remove a node from the story map and save."""
        if node_id in self.story_map:
            del self.story_map[node_id]
            self.save_shared_data()
    
    def _load_project_from_dialog(self):
        """Load a project using a file dialog."""
        filename = filedialog.askopenfilename(
            defaultextension=".cy", 
            filetypes=[("CYOA Files", "*.cy")]
        )
        if filename:
            try:
                # Load project data
                metadata, player_data, story_map, Emoji_Schema = load_cyoa_file(filename)
                self.metadata = Metadata(**metadata)
                # print("Loaded metadata:", self.metadata._asdict(),metadata)
                self.player_data = player_data
                self.story_map = story_map
                self.emoji_schema.current_schema = self.emoji_schema.json_to_text(Emoji_Schema)
                
                messagebox.showinfo("Load", "Project loaded successfully!")
                self._show_project_menu()
                
            except Exception as error:
                messagebox.showerror("Error", f"Failed to load project: {error}")
    
    def cleanup_resources(self):
        """Clean up application resources and stop background threads."""
        self._is_save_thread_running = False
        if hasattr(self, '_background_save_thread'):
            self._background_save_thread.join(timeout=1)


def run_tkinter_editor():
    """Initialize and run the tkinter-based CYOA editor."""
    root = ctk.CTk()
    root.geometry("800x600")
    root.title("CYOA Maker")
    
    application = CYOAMakerApplication(root)
    
    def handle_window_close():
        application.cleanup_resources()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", handle_window_close)
    root.mainloop()
    return application


def main():
    """Main entry point for the application."""
    root = ctk.CTk()
    root.geometry("800x600")
    root.title("CYOA Maker")
    
    application = CYOAMakerApplication(root)
    
    def handle_application_exit():
        application.cleanup_resources()
        root.destroy()
        
        # Clean up shared data file
        if os.path.exists("cyoa_shared_data.pkl"):
            os.remove("cyoa_shared_data.pkl")
        
        # Auto-save on exit if there's content
        if application.story_map:
            filename = filedialog.asksaveasfilename(
                defaultextension=".cyoa", 
                filetypes=[("CYOA Files", "*.cy")]
            )
            if filename:
                try:
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    save_cyoa_file(
                        filename=filename,
                        metadata=application.metadata,
                        player_data=application.player_data,
                        story_map=application.story_map,
                        emoji_schema=application.emoji_schema.get_json_schema()
                    )
                    messagebox.showinfo("Save", "Project saved successfully!")
                except Exception as error:
                    messagebox.showerror("Error", f"Failed to save project: {error}")
    
    root.protocol("WM_DELETE_WINDOW", handle_application_exit)
    root.mainloop()


if __name__ == "__main__":
    main()