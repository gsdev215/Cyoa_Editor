"""
CYOA I/O Module - File operations and data structures for CYOA projects
Handles compression, decompression, and serialization of CYOA story data.
"""

from uuid import uuid4
import zstandard as zstd
import os
import json
from typing import NamedTuple, List, Dict, Any, Tuple
from dataclasses import dataclass


# Predefined story tags for categorization
PREDEFINED_TAGS = [
    'powers simple', 'simple', 'powers', 'comfy', 'humorous',
    'choose multiple', 'mundane', 'dark', 'drawbacks', 'low-level', 'companions',
    'fantasy', 'worldbuilding', 'extensive', 'magic', 'sci-fi', 'themed', 'meta',
    'gear', 'combat', 'survival', 'gift of faves', 'media', 'dragons', 'multiplayer',
    'food & drink', 'political', 'isekai', 'unique', 'apocalyptic', 'family', 'food',
    'realistic', 'medieval', 'farming', 'domain', 'horror', 'artistic', 'rulebreaking',
    'kingdom-building', 'long', 'prison', 'pet', 'franchise', 'rng', 'crime',
    'science-fantasy', 'future', 'western', 'zombies', 'god-like', 'pocket dimension',
    'time', 'trapped', 'dragon', 'adventure', 'school', 'legend', 'history', 'non-fantasy',
    'seasonal', 'abstract', 'werewolf', 'pets', 'planeswalking', 'anime', 'character',
    'superheroes', 'modern', 'weapon', 'runes', 'design', 'time travel', 'mounts', 'roll',
    'home', 'military', 'cute', 'steampunk', 'nsfw text', 'base-building'
]
ENDING_STYLES = {
    # Classic Positive Endings
    "Perfect Ending": ("#81C784", "🌟"),  # success
    "Good Ending": ("#81C784", "✅"),
    "True Ending": ("#D4A373", "🧭"),
    "Peaceful Ending": ("#81C784", "🕊️"),
    "Heroic Ending": ("#D4A373", "🛡️"),
    "Bittersweet Ending": ("#B8B8B8", "🍂"),
    "Enlightenment Ending": ("#F2F2F2", "🧘"),
    "Ascension Ending": ("#F2F2F2", "🌌"),

    # Neutral/Standard Endings
    "Normal Ending": ("#B8B8B8", "📖"),
    "Loop Ending": ("#787878", "🔁"),
    "Ambiguous Ending": ("#B8B8B8", "❔"),
    "Incomplete Ending": ("#787878", "⏳"),
    "Puzzle Ending": ("#D4A373", "🧩"),

    # Negative/Bad Endings
    "Bad Ending": ("#FF6B6B", "⚠️"),
    "Death Ending": ("#FF6B6B", "💀"),
    "Destruction Ending": ("#FF6B6B", "🔥"),
    "Tragic Ending": ("#B8B8B8", "💔"),
    "Corruption Ending": ("#5A5A5A", "😈"),
    "Forgotten Ending": ("#404040", "🕳️"),
    "Locked Ending": ("#404040", "🔒"),

    # Meta/Creative Endings
    "Mindfuck Ending": ("#D4A373", "🌀"),
    "Cutscene Ending": ("#787878", "🎬"),
    "Author Ending": ("#D4A373", "📚"),
    "Box Ending": ("#404040", "📦"),
    "Glitch Ending": ("#5A5A5A", "� glitch"),
    "Xeno Ending": ("#81C784", "👽"),
    "Reset Ending": ("#D4A373", "🔄"),

    # Emotional/Psychological Endings
    "Resignation Ending": ("#787878", "🛑"),
    "Reflection Ending": ("#B8B8B8", "🪞"),
    "Fade Ending": ("#B8B8B8", "🌫️"),
    "Hollow Ending": ("#404040", "🕯️"),
    "Silent Ending": ("#121212", "🤫"),

    # Replayable or Interactive Endings
    "Branch Split Ending": ("#D4A373", "🌿"),
    "Archivist Ending": ("#F2F2F2", "📜"),
    "Tether Ending": ("#D4A373", "⛓️"),
    "Threaded Ending": ("#B8B8B8", "🧵"),
    "Gambler’s Ending": ("#FFD700", "🎲"),

    # Otherworldly or Legendary Endings
    "Ascendant Ending": ("#F2F2F2", "✨"),
    "Mythos Ending": ("#D4A373", "📖"),
    "Legacy Ending": ("#81C784", "🏛️"),
    "Void Ending": ("#121212", "🌑"),
    "Paradox Ending": ("#FF6B6B", "♾️"),

    # Fallback
    "None": ("#404040", "❌"),
}

# UI Theme configuration
UI_THEME = {
    "bg_primary": "#121212",      # Deep charcoal for primary background
    "bg_secondary": "#1E1E1E",   # Slightly lighter charcoal for secondary background
    "accent": "#D4A373",         # Warm beige for accent elements
    "text_primary": "#EDEDED",   # Light gray for primary text
    "text_secondary": "#B8B8B8", # Softer gray for secondary text
    "button_bg": "#5A5A5A",      # Neutral gray for button background
    "button_hover": "#787878",   # Slightly lighter gray for button hover
    "button_text": "#121212",    # Dark text for button readability
    "error": "#FF6B6B",          # Soft red for error messages
    "success": "#81C784",        # Muted green for success
    "choice_bg": "#262626",      # Medium-dark gray for choice backgrounds
    "choice_text": "#F2F2F2",    # Subdued light gray for choice text
    "border": "#404040",         # Border color
    "input_bg": "#262626"        # Input field background
}

ENDINGS = cyoa_endings = {
    "None": "Not an ending",
    # Classic Positive Endings
    "Perfect Ending": "The ideal outcome; all goals achieved, secrets uncovered, and no compromises made.",
    "Good Ending": "A satisfying resolution, though not all objectives may be fulfilled.",
    "True Ending": "The canon or 'intended' ending; often requires specific or hidden choices.",
    "Peaceful Ending": "The conflict is resolved peacefully or nonviolently.",
    "Heroic Ending": "The protagonist sacrifices something or triumphs in a grand way.",
    "Bittersweet Ending": "A mix of happiness and sorrow; gains come with significant loss.",
    "Enlightenment Ending": "The protagonist gains deep understanding or transcends normal outcomes.",
    "Ascension Ending": "The protagonist becomes a legendary or godlike figure.",
    
    # Neutral/Standard Endings
    "Normal Ending": "A typical conclusion based on average choices; neither especially good nor bad.",
    "Loop Ending": "The story ends where it began, often implying a cycle or repetition.",
    "Ambiguous Ending": "Open to interpretation; unclear whether it's good or bad.",
    "Incomplete Ending": "Leaves threads unresolved or sets up a sequel.",
    "Puzzle Ending": "Resolves the plot but leaves a mystery or unanswered question.",
    
    # Negative/Bad Endings
    "Bad Ending": "A failed outcome; major losses, defeat, or irreversible consequences.",
    "Death Ending": "The protagonist dies, often as a direct result of choices.",
    "Destruction Ending": "The world or setting is destroyed, partially or completely.",
    "Tragic Ending": "The protagonist suffers emotionally or loses something dear.",
    "Corruption Ending": "The protagonist becomes evil, corrupted, or loses their morality.",
    "Forgotten Ending": "The protagonist’s efforts are erased, forgotten, or meaningless.",
    "Locked Ending": "A clearly bad or premature ending due to missing critical choices.",
    
    # Meta/Creative Endings
    "Mindfuck Ending": "Reality collapses; nothing was as it seemed. Reader is left questioning everything.",
    "Cutscene Ending": "The story ends with a 'cinematic' monologue or event far outside player control.",
    "Author Ending": "The protagonist meets the author or discovers they’re fictional. Breaks the fourth wall.",
    "Box Ending": "The story ends with the protagonist being sealed away—physically, mentally, or existentially.",
    "Glitch Ending": "The world malfunctions or 'glitches.' Possibly part of a digital simulation or deeper plot.",
    "Xeno Ending": "The protagonist is abducted or spirited away by alien/supernatural forces.",
    "Reset Ending": "The timeline resets, possibly with new knowledge or insight.",
    
    # Emotional/Psychological Endings
    "Resignation Ending": "The protagonist gives up or walks away from their journey. Quiet and heavy.",
    "Reflection Ending": "The protagonist confronts their inner self or past decisions in a final scene.",
    "Fade Ending": "The story dissolves into memory, dream, or stardust. Gentle, ethereal closure.",
    "Hollow Ending": "The goal is achieved, but it feels empty. Emptiness, regret, or apathy dominate.",
    "Silent Ending": "The story ends with no dialogue or explanation. Pure atmosphere or emotion.",
    
    # Replayable or Interactive Endings
    "Branch Split Ending": "The ending literally opens new storylines or games; a fork in the narrative multiverse.",
    "Archivist Ending": "You unlock hidden lore or “true history” that reframes the entire plot.",
    "Tether Ending": "Your actions link this CYOA’s world to another (e.g., a future or past story).",
    "Threaded Ending": "Implies the story continues elsewhere—in books, memory, or secret files.",
    "Gambler’s Ending": "Ends on a risky gamble or coin flip—chance itself decides your fate.",
    
    # Otherworldly or Legendary Endings
    "Ascendant Ending": "You transcend the human plane—becoming a spirit, god, or concept.",
    "Mythos Ending": "Your story becomes legend, distorted by time and passed down.",
    "Legacy Ending": "The story ends years later, showing the world your choices shaped.",
    "Void Ending": "You fall into the unknown—neither dead nor alive, only forgotten.",
    "Paradox Ending": "You cause a time or logic paradox that ends the world—or saves it.",
}


@dataclass
class Metadata:
    """Data class representing CYOA project metadata."""
    
    Author: str
    name: str
    id: str
    description: str
    start: str
    tag: List[str]
    footer: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert the metadata to a dictionary for serialization."""
        return {
            'Author': self.Author,
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'start': self.start,
            'tag': self.tag,
            'footer': self.footer
        }

    # Backward compatibility alias
    def _asdict(self) -> Dict[str, Any]:
        """Legacy alias for to_dict() method."""
        return self.to_dict()


def compress_file_with_zstd(input_filepath: str, output_filepath: str, compression_level: int = 3):
    """
    Compress a file using Zstandard compression.
    
    Args:
        input_filepath: Path to the input file
        output_filepath: Path for the compressed output file
        compression_level: Compression level (1-22, higher = better compression)
    """
    compressor = zstd.ZstdCompressor(level=compression_level)
    
    with open(input_filepath, 'rb') as input_file, \
         open(output_filepath, 'wb') as output_file:
        output_file.write(compressor.compress(input_file.read()))


def decompress_file_with_zstd(input_filepath: str) -> bytes:
    """
    Decompress a Zstandard compressed file.
    
    Args:
        input_filepath: Path to the compressed file
        
    Returns:
        Decompressed file content as bytes
    """
    decompressor = zstd.ZstdDecompressor()
    
    with open(input_filepath, 'rb') as input_file:
        return decompressor.decompress(input_file.read())


def load_cyoa_file(filepath: str) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Load and decompress a CYOA file.
    
    Args:
        filepath: Path to the .cy file
        
    Returns:
        Tuple of (metadata, player_data, story_map)
    """
    decompressed_content = decompress_file_with_zstd(filepath)
    project_data = json.loads(decompressed_content)
    
    return (
        project_data['metadata'], 
        project_data['playerdata'], 
        project_data['storymap'],
        project_data['EmojiSchema']
    )


def save_cyoa_file(filename: str, metadata: Metadata, player_data: Dict[str, Any], story_map: Dict[str, Any], emoji_schema: Dict[str, Any]):
    """
    Compress and save CYOA project data to a .cy file.
    
    Args:
        filename: Output filename (without extension)
        metadata: Project metadata
        player_data: Player/game data
        story_map: Story node data
    """
    # Convert metadata to dictionary format
    metadata_dict = metadata.to_dict()
    
    # Prepare complete project data
    project_data = {
        'metadata': metadata_dict,
        'playerdata': player_data,
        'storymap': story_map,
        'EmojiSchema': emoji_schema
    }
    
    # Serialize to JSON and encode
    serialized_data = json.dumps(project_data, indent=2).encode('utf-8')
    compressor = zstd.ZstdCompressor(level=3)
    
    # Ensure output directory exists
    output_directory = 'storys'
    os.makedirs(output_directory, exist_ok=True)
    
    # Generate output file path
    clean_filename = filename.replace(".cy", "")
    output_filepath = os.path.join(output_directory, f'{clean_filename}.cy')
    
    # Write compressed data
    with open(output_filepath, 'wb') as output_file:
        output_file.write(compressor.compress(serialized_data))
    
    print(f"CYOA project saved to: {output_filepath}")


# Legacy function aliases for backward compatibility
def open_cy(filepath: str):
    """Legacy alias for load_cyoa_file()."""
    return load_cyoa_file(filepath)


def write_to_cy(filename: str, metadata: Metadata, playerdata: Dict[str, Any], storymap: Dict[str, Any], EmojiSchema : Dict[str, Any]):
    """Legacy alias for save_cyoa_file()."""
    return save_cyoa_file(filename, metadata, playerdata, storymap , EmojiSchema)


# Legacy variable aliases for backward compatibility
tags = PREDEFINED_TAGS
THEME = UI_THEME