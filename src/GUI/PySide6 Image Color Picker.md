# PySide6 Image Color Picker

A Python-based GUI application for picking colors from images with a magnifying glass for precision, featuring color exclusion capabilities.

## Features
- **Image Upload**: Load any standard image format (PNG, JPG, BMP, etc.).
- **Color Picking**: Click anywhere on the image to capture the color.
- **Magnifier**: A real-time magnifying glass follows your cursor to help you pick the exact pixel.
- **Color List**: Displays captured colors with their RGB and Hexadecimal values.
- **Color Exclusion**: Mark colors as 'excluded from trace' to visually distinguish them and filter them programmatically. Excluded colors appear grayed out and struck through.
- **Management**: Easily delete individual colors, toggle their exclusion status, or clear the entire list.
- **Programmatic Access**: The color list is managed by a standalone `ColorModel` class that saves to `colors.json`, allowing other programs to interact with the data.

## Project Structure
- `main.py`: The main PySide6 application.
- `color_model.py`: The core logic for managing and persisting the color list.
- `test_interaction.py`: A demonstration of how to interact with the color list programmatically.
- `colors.json`: The persistent storage for your selected colors.

## Installation
Ensure you have Python 3.11+ and PySide6 installed:
```bash
pip install PySide6
```

## Usage
1. Run the application:
   ```bash
   python main.py
   ```
2. Click **Upload Image** to load a picture.
3. Hover over the image to see the magnified view.
4. Click to add a color to the list on the right.
5. Click the **✕** icon next to a color to remove it.
6. Click the **Exclude/Include** button next to a color to toggle its exclusion status.

## Programmatic Interaction
You can use the `ColorModel` in your other scripts to read or modify the color list:

```python
from color_model import ColorModel

model = ColorModel()
active_colors = model.get_active_colors()
print("Active Colors:", active_colors)
```
