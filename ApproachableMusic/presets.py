import os
import json

# Default preset parameters
DEFAULT_PRESET = [
    # Sine
    {'enable': True, 'volume': 46, 'duration': 1282, 'delay': 43, 'fade_in': 232, 'fade_out': 1211},
    # Square
    {'enable': True, 'volume': 2, 'duration': 2418, 'delay': 251, 'fade_in': 772, 'fade_out': 500},
    # Sawtooth
    {'enable': True, 'volume': 4, 'duration': 2439, 'delay': 105, 'fade_in': 286, 'fade_out': 1488},
    # Triangle
    {'enable': True, 'volume': 25, 'duration': 3471, 'delay': 939, 'fade_in': 438, 'fade_out': 1089}
]

# Additional preset templates
PRESET_TEMPLATES = {
    "Bright": [
        {'enable': True, 'volume': 60, 'duration': 1000, 'delay': 0, 'fade_in': 50, 'fade_out': 200},
        {'enable': True, 'volume': 15, 'duration': 800, 'delay': 50, 'fade_in': 100, 'fade_out': 300},
        {'enable': True, 'volume': 20, 'duration': 900, 'delay': 25, 'fade_in': 75, 'fade_out': 250},
        {'enable': True, 'volume': 40, 'duration': 1200, 'delay': 10, 'fade_in': 150, 'fade_out': 400}
    ],
    "Soft": [
        {'enable': True, 'volume': 50, 'duration': 2000, 'delay': 0, 'fade_in': 500, 'fade_out': 1000},
        {'enable': False, 'volume': 0, 'duration': 1000, 'delay': 0, 'fade_in': 200, 'fade_out': 500},
        {'enable': False, 'volume': 0, 'duration': 1000, 'delay': 0, 'fade_in': 200, 'fade_out': 500},
        {'enable': True, 'volume': 30, 'duration': 2500, 'delay': 100, 'fade_in': 600, 'fade_out': 1200}
    ],
    "Punchy": [
        {'enable': True, 'volume': 30, 'duration': 800, 'delay': 0, 'fade_in': 10, 'fade_out': 400},
        {'enable': True, 'volume': 25, 'duration': 600, 'delay': 0, 'fade_in': 5, 'fade_out': 200},
        {'enable': True, 'volume': 20, 'duration': 700, 'delay': 0, 'fade_in': 5, 'fade_out': 300},
        {'enable': True, 'volume': 15, 'duration': 900, 'delay': 0, 'fade_in': 20, 'fade_out': 500}
    ]
}

# Determine the directory of the current script to locate presets.json
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_PRESETS_FILE = os.path.join(_BASE_DIR, "presets.json")

class PresetManager:
    """Manages presets for the music generator, loading from and saving to presets.json"""
    
    def __init__(self):
        self.presets = {}
        self._load_presets()
        
    def _load_presets(self):
        """Load presets from presets.json, or initialize with defaults if not found/invalid."""
        try:
            if os.path.exists(_PRESETS_FILE):
                with open(_PRESETS_FILE, 'r') as f:
                    self.presets = json.load(f)
                # Ensure "Default" preset exists, using DEFAULT_PRESET if it was somehow removed
                if "Default" not in self.presets:
                    self.presets["Default"] = DEFAULT_PRESET.copy()
                    self._save_presets() # Save if we had to add Default
                return
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading presets file ({_PRESETS_FILE}): {e}. Initializing with defaults.")
            # Fallthrough to initialize with defaults
        
        # Initialize with default presets if file doesn't exist or was invalid
        self.presets = {
            "Default": DEFAULT_PRESET.copy(),
            "Bright": PRESET_TEMPLATES["Bright"].copy(),
            "Soft": PRESET_TEMPLATES["Soft"].copy(),
            "Punchy": PRESET_TEMPLATES["Punchy"].copy()
        }
        self._save_presets() # Create the presets.json file with initial defaults

    def _save_presets(self):
        """Save the current presets to presets.json."""
        try:
            with open(_PRESETS_FILE, 'w') as f:
                json.dump(self.presets, f, indent=4)
        except IOError as e:
            print(f"Error saving presets file ({_PRESETS_FILE}): {e}")

    def get_preset(self, name):
        """Get a preset by name. Returns a copy of the default preset if name not found."""
        if name in self.presets:
            return self.presets[name].copy() # Return a copy to prevent direct modification
        # Fallback for safety, though UI should generally only request existing names
        print(f"Warning: Preset '{name}' not found in manager. Returning a copy of 'Default'.")
        return DEFAULT_PRESET.copy() 
    
    def save_preset(self, name, preset_data):
        """Save a preset with the given name and persist to file."""
        self.presets[name] = preset_data.copy() # Store a copy
        self._save_presets()
        
    def get_preset_names(self):
        """Get a list of all preset names, ensuring "Default" is first if it exists."""
        names = list(self.presets.keys())
        if "Default" in names:
            names.remove("Default")
            names.insert(0, "Default")
        return names
    
    def delete_preset(self, name):
        """Delete a preset by name and persist changes. Cannot delete "Default"."""
        if name in self.presets and name != "Default":
            del self.presets[name]
            self._save_presets()
            return True
        return False
    
    def reset_preset(self, name):
        """Reset a preset to its default template if available and persist."""
        original_preset = None
        if name == "Default":
            original_preset = DEFAULT_PRESET.copy()
        elif name in PRESET_TEMPLATES:
            original_preset = PRESET_TEMPLATES[name].copy()
        
        if original_preset:
            self.presets[name] = original_preset
            self._save_presets()
            return True
        return False
