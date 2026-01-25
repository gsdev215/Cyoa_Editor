"""
Streamlit Web Interface for CYOA Story Map Visualization
Provides a web-based interface to visualize and interact with CYOA story structures.
"""

import streamlit as st
import multiprocessing
import time
import graphviz
import pickle
import os
from typing import Dict, Any, Optional, Set
from TkApp import run_tkinter_editor


# Configuration constants
SHARED_DATA_FILEPATH = "cyoa_shared_data.pkl"
COMMAND_FILE_PATH = "cyoa_commands.pkl"

# Global process variable
editor_process = None


def load_shared_project_data() -> Dict[str, Any]:
    """
    Load project data from the shared data file.
    
    Returns:
        Dictionary containing story map, player data, and metadata
    """
    try:
        if os.path.exists(SHARED_DATA_FILEPATH):
            with open(SHARED_DATA_FILEPATH, 'rb') as file:
                return pickle.load(file)
    except Exception as error:
        st.error(f"Error loading shared project data: {error}")
    
    # Return empty structure if loading fails
    return {
        "storymap": {}, 
        "playerdata": {}, 
        "metadata": {}
    }


def create_story_graph_visualization(story_map: Dict[str, Any]) -> str:
    """
    Create a Graphviz DOT graph representation of the story map.
    
    Args:
        story_map: Dictionary containing story node data
        
    Returns:
        Graphviz DOT source code as string
    """
    if not story_map:
        return """digraph empty_graph { 
            bgcolor="transparent"
            label="No story data available\\nStart the editor to create your story"
            labelloc="c"
            fontsize="16"
            fontcolor="gray"
        }"""
    
    # Initialize graph
    graph = graphviz.Digraph(comment='CYOA Story Structure')
    
    # Configure graph appearance
    graph.attr(
        rankdir='TB',           # Top to bottom layout
        bgcolor='transparent',  # Transparent background
        fontname='Arial',
        nodesep='0.5',         # Space between nodes
        ranksep='0.8'          # Space between ranks
    )
    
    # Configure node styling
    graph.attr('node',
        shape='box',
        style='filled',
        fontname='Arial',
        fontsize='10'
    )
    
    # Configure edge styling
    graph.attr('edge',
        fontname='Arial',
        fontsize='9'
    )
    
    # Collect all node IDs (including referenced but missing nodes)
    all_node_ids = _collect_all_node_references(story_map)
    
    # Add nodes to graph
    _add_nodes_to_graph(graph, story_map, all_node_ids)
    
    # Add edges (connections between nodes)
    _add_edges_to_graph(graph, story_map)
    
    return graph.source


def _collect_all_node_references(story_map: Dict[str, Any]) -> Set[str]:
    """
    Collect all node IDs referenced in the story map.
    
    Args:
        story_map: Dictionary containing story node data
        
    Returns:
        Set of all node IDs (existing and referenced)
    """
    all_node_ids = set(story_map.keys())
    
    for node_data in story_map.values():
        if isinstance(node_data, dict):
            choices = node_data.get('choices', [])
            for choice in choices:
                if isinstance(choice, dict):
                    target_id = choice.get('id', '')
                    if target_id:
                        all_node_ids.add(target_id)
    
    return all_node_ids


def _add_nodes_to_graph(graph: graphviz.Digraph, story_map: Dict[str, Any], all_node_ids: Set[str]):
    """
    Add all nodes to the graph with appropriate styling.
    
    Args:
        graph: Graphviz graph object
        story_map: Dictionary containing story node data
        all_node_ids: Set of all node IDs to add
    """
    for node_id in all_node_ids:
        if node_id in story_map:
            _add_existing_node(graph, node_id, story_map[node_id])
        else:
            _add_missing_node(graph, node_id)


def _add_existing_node(graph: graphviz.Digraph, node_id: str, node_data: Dict[str, Any]):
    """
    Add an existing story node to the graph.
    
    Args:
        graph: Graphviz graph object
        node_id: Node identifier
        node_data: Node data dictionary
    """
    choices = node_data.get('choices', []) if isinstance(node_data, dict) else []
    
    # Create node label with truncated description
    description = node_data.get('description', '')
    truncated_description = description.split('\n')[0][:17]
    node_label = f"{node_id}\\n{truncated_description}"
    
    # Color code based on number of choices
    if not choices:
        # End node (no choices)
        graph.node(node_id, node_label, fillcolor='lightcoral')
    elif len(choices) == 1:
        # Single choice node
        graph.node(node_id, node_label, fillcolor='lightyellow')
    else:
        # Multiple choice node
        graph.node(node_id, node_label, fillcolor='lightblue')


def _add_missing_node(graph: graphviz.Digraph, node_id: str):
    """
    Add a placeholder for a missing/referenced node.
    
    Args:
        graph: Graphviz graph object
        node_id: Node identifier
    """
    node_label = f"{node_id}\\n(missing)"
    graph.node(node_id, node_label, fillcolor='lightgray', style='filled,dashed')


def _add_edges_to_graph(graph: graphviz.Digraph, story_map: Dict[str, Any]):
    """
    Add edges (choice connections) to the graph.
    
    Args:
        graph: Graphviz graph object
        story_map: Dictionary containing story node data
    """
    for node_id, node_data in story_map.items():
        if not isinstance(node_data, dict):
            continue
        
        choices = node_data.get('choices', [])
        if not isinstance(choices, list):
            continue
        
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            
            target_id = choice.get('id', '')
            choice_text = choice.get('text', '')
            
            if target_id:
                # Truncate choice text for display
                display_label = choice_text[:17] if choice_text else "Choice"
                graph.edge(node_id, target_id, label=display_label, fontcolor='lightblue')


def start_editor_process() -> bool:
    """
    Start the CYOA editor in a separate process.
    
    Returns:
        True if editor was started, False if already running
    """
    global editor_process
    
    if editor_process is None or not editor_process.is_alive():
        editor_process = multiprocessing.Process(target=run_tkinter_editor)
        editor_process.start()
        return True
    
    return False


def send_command_to_editor(command_data: Dict[str, Any]) -> bool:
    """
    Send a command to the editor via the shared command file.
    
    Args:
        command_data: Dictionary containing command information
        
    Returns:
        True if command was sent successfully, False otherwise
    """
    try:
        command_data["timestamp"] = time.time()
        with open(COMMAND_FILE_PATH, 'wb') as file:
            pickle.dump(command_data, file)
        return True
    except Exception as error:
        st.error(f"Error sending command to editor: {error}")
        return False


def send_edit_node_command(node_id: str) -> bool:
    """
    Send an edit node command to the editor.
    
    Args:
        node_id: ID of the node to edit
        
    Returns:
        True if command was sent successfully
    """
    command_data = {
        "command": "edit_node",
        "node_id": node_id
    }
    return send_command_to_editor(command_data)


def send_save_command() -> bool:
    """
    Send a save command to the editor.
    
    Returns:
        True if command was sent successfully
    """
    command_data = {"command": "Save"}
    return send_command_to_editor(command_data)


def create_control_panel():
    """Create the main control panel with buttons and options."""
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
    
    with col1:
        if st.button("🚀 Start Editor"):
            if start_editor_process():
                st.session_state.editor_running = True
                st.success("Editor started successfully!")
            else:
                st.warning("Editor is already running!")
    
    with col2:
        auto_refresh_enabled = st.checkbox(
            "Auto-refresh", 
            value=st.session_state.get('auto_refresh', True)
        )
        st.session_state.auto_refresh = auto_refresh_enabled
    
    with col3:
        if st.button("💾 Save Project"):
            if send_save_command():
                st.success("Save command sent to editor!")
            else:
                st.error("Failed to send save command!")
    
    with col4:
        if st.button("🔄 Refresh View"):
            st.rerun()
    
    with col5:
        _create_node_selector()


def _create_node_selector():
    """Create the node selection dropdown and edit button."""
    # Load current data to populate node options
    project_data = load_shared_project_data()
    current_story_map = project_data.get("storymap", {})
    
    if current_story_map:
        node_options = [""] + list(current_story_map.keys())
        selected_node = st.selectbox(
            "Edit Node by ID:",
            options=node_options,
            format_func=lambda x: f"Node {x}" if x else "Select node..."
        )
        
        if selected_node and st.button("✏️ Edit Selected"):
            if send_edit_node_command(selected_node):
                st.success(f"Edit command sent for node: {selected_node}")
            else:
                st.error("Failed to send edit command!")


def display_story_visualization():
    """Display the main story map visualization."""
    project_data = load_shared_project_data()
    current_story_map = project_data.get("storymap", {})
    
    if current_story_map:
        try:
            # Generate and display the graph
            graph_source = create_story_graph_visualization(current_story_map)
            st.graphviz_chart(graph_source, width='stretch')
            # Display project statistics
            _display_project_statistics(project_data)
            
        except Exception as error:
            st.error(f"Error creating story visualization: {error}")
    else:
        st.info("📝 No story data available. Start the editor to begin creating your story!")


def _display_project_statistics(project_data: Dict[str, Any]):
    """
    Display basic project statistics.
    
    Args:
        project_data: Dictionary containing project information
    """
    story_map = project_data.get("storymap", {})
    metadata = project_data.get("metadata", {})
    
    if story_map or metadata:
        st.sidebar.header("📊 Project Statistics")
        
        # Basic counts
        node_count = len(story_map)
        st.sidebar.metric("Total Nodes", node_count)
        
        # Choice statistics
        total_choices = sum(
            len(node.get('choices', [])) 
            for node in story_map.values() 
            if isinstance(node, dict)
        )
        st.sidebar.metric("Total Choices", total_choices)
        
        # Project metadata
        if metadata:
            st.sidebar.header("📋 Project Info")
            if title := metadata.get("title"):
                st.sidebar.text(f"Title: {title}")
            if author := metadata.get("author"):
                st.sidebar.text(f"Author: {author}")
            if description := metadata.get("description"):
                st.sidebar.text(f"Description: {description[:50]}...")


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'editor_running' not in st.session_state:
        st.session_state.editor_running = False
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True


def configure_page():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="CYOA Story Map Visualizer",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def main():
    """Main application entry point."""
    configure_page()
    initialize_session_state()
    
    # Page header
    st.title("📚 CYOA Story Map Visualizer")
    st.markdown("*Visualize and navigate your Choose Your Own Adventure stories*")
    
    # Main control panel
    create_control_panel()
    
    # Add some spacing
    st.markdown("---")
    
    # Main visualization area
    display_story_visualization()
    
    # Auto-refresh functionality
    if st.session_state.auto_refresh:
        time.sleep(2)
        st.rerun()


if __name__ == "__main__":
    main()