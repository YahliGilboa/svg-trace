import json
import os

class ColorModel:
    """
    A model to manage a list of colors with an 'excluded' state.
    Each color is stored as a dictionary: 
    {
        'rgb': (r, g, b), 
        'hex': '#rrggbb',
        'excluded': bool
    }
    """
    def __init__(self, storage_file="colors.json"):
        self.colors = []
        self.storage_file = storage_file
        self.callbacks = []
        self.load()

    def add_color(self, r, g, b, excluded=False):
        hex_val = f"#{r:02x}{g:02x}{b:02x}".upper()
        color_data = {
            'rgb': (r, g, b),
            'hex': hex_val,
            'excluded': excluded
        }
        
        # Check if color already exists (ignoring excluded state for duplication check)
        for existing in self.colors:
            if existing['rgb'] == (r, g, b):
                return existing
                
        self.colors.append(color_data)
        self.save()
        self._notify()
        return color_data

    def toggle_exclude(self, index):
        if 0 <= index < len(self.colors):
            self.colors[index]['excluded'] = not self.colors[index]['excluded']
            self.save()
            self._notify()
            return self.colors[index]
        return None

    def remove_color(self, index):
        if 0 <= index < len(self.colors):
            removed = self.colors.pop(index)
            self.save()
            self._notify()
            return removed
        return None

    def get_colors(self):
        return self.colors

    def get_active_colors(self):
        return [c for c in self.colors if not c['excluded']]

    def get_excluded_colors(self):
        return [c for c in self.colors if c['excluded']]

    def clear(self):
        self.colors = []
        self.save()
        self._notify()

    def save(self):
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.colors, f, indent=4)
        except Exception as e:
            print(f"Error saving colors: {e}")

    def load(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    self.colors = json.load(f)
            except Exception as e:
                print(f"Error loading colors: {e}")
                self.colors = []

    def register_callback(self, callback):
        """Register a function to be called whenever the color list changes."""
        self.callbacks.append(callback)

    def _notify(self):
        for callback in self.callbacks:
            callback(self.colors)

if __name__ == "__main__":
    model = ColorModel()
    print("Current colors:", model.get_colors())
