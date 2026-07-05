# Starry Night - Celestial Viewer Usage Guide

## Overview
Starry Night is a desktop planetarium that shows the real night sky for your location. The sky rotates with (simulated) time, the Sun/Moon/planets follow real ephemerides, and you can click any object for details.

## Features
- Real star positions (J2000 catalog) with 21 constellation figures
- Sun, Moon (with phase), and all seven planets from real ephemerides
- Day/night cycle with twilight colors; stars fade with the brightening sky (toggle "always night" with N to keep the sky dark)
- Time playback from real-time up to a month per second
- Linux installer support

## Installation

### Method 1: Using the installer script
```bash
# Make the installer executable
chmod +x install.sh

# Run the installer
./install.sh
```

### Method 2: Manual installation
```bash
# Create a virtual environment
python -m venv starry_night_env

# Activate the virtual environment
source starry_night_env/bin/activate

# Install the application
pip install -e .

# Run the application
python -m starry_night
```

## Running the Application

### From terminal
```bash
# Activate virtual environment (if using manual installation)
source starry_night_env/bin/activate

# Run the application
python -m starry_night
```

### Using the desktop launcher
After installation, you can run the application from your desktop environment's application menu or by typing:
```bash
starry-night
```

## Using the Application

1. The application opens in a resizable window showing the sky as it looks right now from your location (default: Amsterdam; use `--lat`/`--lon` for elsewhere), with a horizon line and N/E/S/W markers
2. **Look around** by clicking and dragging the mouse (the sky follows your mouse) or with the arrow keys
3. **Zoom** with the scroll wheel
4. **Hover** over any celestial object for a quick tooltip; **click** it for a detail panel with:
   - Object name, type, and constellation
   - Distance from Earth (light-years, AU for planets, km for the Moon)
   - Magnitude (brightness) and current azimuth/altitude
   - The Moon additionally shows its phase and illumination
5. **Play time** with SPACE and change speed with + / -; the sky rotates as the Earth turns, the Moon cycles through phases, and planets wander. R resets the time
6. Other keys: K toggles constellation figures, N toggles "always night" (dark sky even in daytime), L toggles labels, T hides/shows the selected object, C toggles the control panel, ESC deselects (or quits when nothing is selected)

## Customization

The application currently comes with a predefined set of celestial objects. To customize:
1. Modify `starry_night/main.py` 
2. Add more objects to the `create_celestial_objects()` method
3. Reinstall the application

## Requirements
- Python 3.8 or higher
- Pygame 2.0.0 or higher

## Troubleshooting

### If you get "command not found" error
Make sure the application is properly installed and that the PATH includes the directory where the launcher script is installed.

### If you get pygame errors
Make sure you have all the required dependencies installed:
```bash
pip install pygame
```

### If the application doesn't start
Try running with Python directly:
```bash
python -m starry_night
```