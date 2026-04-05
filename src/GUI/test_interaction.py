from color_model import ColorModel
import time

def main():
    # Initialize the model
    model = ColorModel()
    model.clear() # Start fresh for the test
    
    print("--- Programmatic Interaction Test ---")
    
    # Add some colors
    print("Adding Red, Green, and Blue...")
    model.add_color(255, 0, 0)   # Red
    model.add_color(0, 255, 0)   # Green
    model.add_color(0, 0, 255)   # Blue
    
    # Exclude Green
    print("Excluding Green (index 1)...")
    model.toggle_exclude(1)
    
    # Show all colors
    print("\nAll Colors in Model:")
    for i, color in enumerate(model.get_colors()):
        status = "[EXCLUDED]" if color['excluded'] else "[ACTIVE]"
        print(f"{i}: {status} RGB {color['rgb']} | Hex {color['hex']}")
    
    # Show only active colors
    print("\nActive Colors (for tracing):")
    for color in model.get_active_colors():
        print(f"-> RGB {color['rgb']} | Hex {color['hex']}")

    # Show only excluded colors
    print("\nExcluded Colors:")
    for color in model.get_excluded_colors():
        print(f"-> RGB {color['rgb']} | Hex {color['hex']}")

    # Re-include Green
    print("\nRe-including Green...")
    model.toggle_exclude(1)
    print(f"Green is now excluded: {model.get_colors()[1]['excluded']}")

if __name__ == "__main__":
    main()
