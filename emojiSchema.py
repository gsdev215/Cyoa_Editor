import json

class EmojiSchema:
    def __init__(self):
        # Default schema
        self.default_schema = "A -> 🇦\nB -> 🇧\nC -> 🇨\nD -> 🇩"
        self.current_schema = self.default_schema

    def text_to_json(self, text_schema=None):
        """Convert text format to JSON/dictionary"""
        if text_schema is None:
            text_schema = self.current_schema
        
        lines = [line.strip() for line in text_schema.split('\n') if line.strip()]
        json_obj = {}
        
        for line in lines:
            parts = [part.strip() for part in line.split('->')]
            if len(parts) == 2:
                variable, emoji = parts
                json_obj[variable] = emoji
        
        return json_obj

    def json_to_text(self, json_obj):
        """Convert JSON/dictionary back to text format"""
        lines = []
        for variable, emoji in json_obj.items():
            lines.append(f"{variable} -> {emoji}")
        return '\n'.join(lines)

    def update_schema(self, new_schema):
        """Update the current schema"""
        self.current_schema = new_schema

    def get_text_schema(self):
        """Get current schema in text format"""
        return self.current_schema

    def get_json_schema(self):
        """Get current schema in JSON format"""
        return self.text_to_json()

    def reset_to_default(self):
        """Reset to default schema"""
        self.current_schema = self.default_schema

    def set_mapping(self, variable, emoji):
        """Add or update a single mapping"""
        json_schema = self.text_to_json()
        json_schema[variable] = emoji
        self.current_schema = self.json_to_text(json_schema)

    def remove_mapping(self, variable):
        """Remove a mapping"""
        json_schema = self.text_to_json()
        if variable in json_schema:
            del json_schema[variable]
            self.current_schema = self.json_to_text(json_schema)

    def get_emoji(self, variable):
        """Get emoji for a variable"""
        json_schema = self.text_to_json()
        return json_schema.get(variable)

    def save_to_json_file(self, filename):
        """Save current schema to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.get_json_schema(), f, ensure_ascii=False, indent=2)

    def load_from_json_file(self, filename):
        """Load schema from JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            json_obj = json.load(f)
            self.current_schema = self.json_to_text(json_obj)

# Example usage:
if __name__ == "__main__":
    # Create emoji schema instance
    emoji_schema = EmojiSchema()

    print("Default schema (text):")
    print(emoji_schema.get_text_schema())
    print()

    print("Default schema (JSON):")
    print(json.dumps(emoji_schema.get_json_schema(), ensure_ascii=False, indent=2))
    print()

    # Add new mappings
    emoji_schema.set_mapping("E", "🇪")
    emoji_schema.set_mapping("HEART", "❤️")
    
    print("After adding E and HEART:")
    print(emoji_schema.get_text_schema())
    print()

    # Convert to JSON
    json_version = emoji_schema.get_json_schema()
    print("JSON version:")
    print(json.dumps(json_version, ensure_ascii=False, indent=2))
    print()

    # Convert back to text
    text_version = emoji_schema.json_to_text(json_version)
    print("Converted back to text:")
    print(text_version)
    print()

    # Test individual functions
    print("Get emoji for 'A':", emoji_schema.get_emoji("A"))
    print("Get emoji for 'HEART':", emoji_schema.get_emoji("HEART"))
    
    # Remove a mapping
    emoji_schema.remove_mapping("B")
    print("\nAfter removing 'B':")
    print(emoji_schema.get_text_schema())