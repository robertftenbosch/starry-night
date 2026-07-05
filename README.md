# Starry Night - Celestial Viewer

A desktop application that displays celestial objects in a dome-like starry night visualization with interactive controls and time playback capabilities.

## Features

- **True 3D Sky Sphere**: Objects live on a celestial sphere (azimuth/altitude) and are projected through a real camera, so rotating and zooming actually move the sky
- **Celestial Objects**: Background stars, planets, notable stars, and galaxies
- **Time Playback**: Play through time with adjustable speeds (real-time up to 1 year/s); planets drift along the sky according to their orbital periods
- **Mouse & Keyboard Navigation**: Drag (or use the arrow keys) to look around, scroll to zoom
- **Object Selection**: Click any object for a detail panel; hover for a quick tooltip
- **Horizon & Compass**: A horizon line with N/E/S/W markers plus a compass that rotates with your viewing direction
- **Resizable Window**: The view adapts when you resize the window

## Installation

### Prerequisites
Before installing, make sure you have the following system dependencies:
- Python 3.8 or higher
- SDL2 development libraries

### Installing SDL2 Dependencies
On Debian/Ubuntu systems:
```bash
sudo apt-get update
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

On Red Hat/CentOS/Fedora systems:
```bash
sudo yum install SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel
```

On Fedora systems:
```bash
sudo dnf install SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel
```

### Installing Starry Night
You can install Starry Night using the provided installer script:

```bash
# Make the installer executable
chmod +x install.sh

# Run the installer
./install.sh
```

Alternatively, you can install manually:
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
After installation, run the application with:
```bash
starry-night
```

## Usage Instructions

### Controls
- **Mouse drag / Arrow keys**: Look around (rotate the view)
- **Scroll wheel**: Zoom in/out
- **Click**: Select an object and show its detail panel
- **Spacebar**: Start/pause time playback
- **+ / -**: Change time speed
- **R**: Reset to start time
- **T**: Toggle visibility of the selected object
- **L**: Toggle object labels
- **C**: Toggle the control panel
- **ESC**: Deselect object, or quit when nothing is selected

### Navigation
1. **View Rotation**: Click and drag with the mouse (or use the arrow keys) — the sky follows your mouse
2. **Zoom**: Use the scroll wheel to zoom between wide-angle and close-up views
3. **Time Playback**: Press SPACE and adjust the speed with + / - to watch planets drift along the sky
4. **Object Selection**: Click on celestial objects to see distance, magnitude, and orbital data
5. **Orientation**: Use the horizon markers (N/E/S/W) and the compass in the top-right corner; the compass rotates with your viewing direction

### Information Display
- Hover over any celestial object to see its name and information
- Additional details are displayed when hovering over objects
- Current time and playback speed are shown in the top-left corner

## Customization

The application can be customized by modifying:
- `starry_night/main.py` to add more celestial objects
- Object properties to change appearance or behavior
- Time scales and orbital mechanics

## Requirements
- Python 3.8 or higher
- Pygame 2.0.0 or higher
- Requests library
- NumPy 1.20.0 or higher

## Troubleshooting

### If you get "command not found" error
Make sure the application is properly installed and that the PATH includes the directory where the launcher script is installed.

### If you get pygame errors
Make sure you have all the required dependencies installed:
```bash
pip install pygame requests numpy
```

### If the application doesn't start
Try running with Python directly:
```bash
python -m starry_night
```

## Project Structure
```
starry_night/
├── starry_night/              # Main application package
│   ├── __init__.py
│   ├── __main__.py
│   └── main.py               # Main application logic
├── install.sh                # Linux installer script
├── setup.py                  # Python package configuration
├── requirements.txt          # Required dependencies
├── README.md                 # This file
└── USAGE.md                  # Detailed usage instructions
```

## License
MIT License

## Author
Starry Night Developer

## Acknowledgements
- Built with Python and Pygame
- Inspired by real astronomical data and visualization techniques