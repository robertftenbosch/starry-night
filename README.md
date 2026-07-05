# Starry Night - Celestial Viewer

A desktop planetarium that shows the real night sky for your location, with interactive navigation and time playback.

## Features

- **The Real Sky**: Stars come from a catalog with true J2000 coordinates; the whole sky rotates with (simulated) time as the Earth turns, matching what you would actually see outside
- **Constellations**: Stick figures and names for 21 well-known constellations (Orion, Ursa Major, Cassiopeia, Cygnus, Crux, ...)
- **Sun, Moon & Planets**: Computed from real ephemerides — the Moon shows its current phase, and all seven planets follow their Keplerian orbits
- **Deep-Sky Objects**: 26 showpieces (Orion Nebula, Pleiades, Hercules Cluster, Ring Nebula, ...) with type-specific rendering for nebulae, clusters, and galaxies
- **Search & Go-To**: Press S, type a name or Messier number ("M42", "Jupiter", "Orion"), and the camera glides to it
- **Follow Mode**: Press F to lock the camera on the selected object while time plays — follow the Moon through its phases for a month
- **Jump to Date/Time**: Press D and enter any date to see that night's sky ("the sky on my birthday")
- **Rise & Set Times**: The detail panel shows when the selected object rises and sets today
- **Milky Way**: A faint band of glow along the galactic plane
- **Sky Grids & Ecliptic**: Press G to cycle an alt/az grid or an RA/Dec grid with the ecliptic
- **Meteor Showers**: Shooting stars from the radiant around shower peaks (Perseids, Geminids, Quadrantids, ...)
- **Day/Night Cycle**: The sky brightens through dawn, turns blue at day, and glows orange at sunset; stars fade in and out with twilight (press N for "always night" to keep the sky dark)
- **Night Vision**: Press V for a red-light mode that preserves your dark adaptation at the telescope
- **Time Playback**: Play through time from real-time up to a month per second — watch stars rise and set, the Moon cycle through phases, and planets wander
- **Mouse & Keyboard Navigation**: Drag (or use the arrow keys) to look around, scroll to zoom
- **Object Selection**: Click any object for a detail panel; hover for a quick tooltip
- **Horizon & Compass**: A horizon line with N/E/S/W markers plus a compass that rotates with your viewing direction
- **Observer Location**: Defaults to Amsterdam; set your own with `--lat` and `--lon`

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

By default the sky is computed for Amsterdam. For another location, pass your coordinates (degrees, east/north positive):
```bash
starry-night --lat 40.7 --lon -74.0   # New York
```

## Usage Instructions

### Controls
- **Mouse drag / Arrow keys**: Look around (rotate the view)
- **Scroll wheel**: Zoom in/out
- **Click**: Select an object and show its detail panel
- **S or /**: Search an object or constellation and glide to it (type, pick with UP/DOWN, ENTER)
- **F**: Follow the selected object (camera stays locked while time plays)
- **D**: Jump to a date/time (`YYYY-MM-DD [HH:MM]`, local time)
- **Spacebar**: Start/pause time playback
- **+ / -**: Change time speed
- **R**: Reset to start time
- **G**: Cycle sky grids: off → alt/az grid → RA/Dec grid + ecliptic
- **K**: Toggle constellation figures and names
- **N**: Toggle "always night" — keeps the sky dark and the stars visible even in daytime
- **V**: Toggle night vision (red-light mode)
- **L**: Toggle object labels
- **T**: Toggle visibility of the selected object
- **C**: Toggle the control panel
- **ESC**: Stop following / deselect / quit

### Navigation
1. **View Rotation**: Click and drag with the mouse (or use the arrow keys) — the sky follows your mouse
2. **Zoom**: Use the scroll wheel to zoom between wide-angle and close-up views
3. **Time Playback**: Press SPACE and adjust the speed with + / - to watch the sky rotate, the Moon change phase, and planets wander along the ecliptic
4. **Object Selection**: Click on celestial objects to see constellation, distance, magnitude, and current azimuth/altitude
5. **Orientation**: Use the horizon markers (N/E/S/W) and the compass in the top-right corner; the compass rotates with your viewing direction

### Tips
- Around midnight, look south for the season's constellations (Orion in winter, Cygnus and Lyra in summer)
- Search "M42" and zoom in on the Orion Nebula, or search "Pleiades" for the Seven Sisters
- Select the Moon, press F to follow it, set the speed to "1 day/s", and watch it race through its phases
- Jump to August 12 (D key) for the Perseid meteor shower
- The status bar shows the sun's altitude and the current moon phase

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

## Project Structure
```
starry_night/
├── starry_night/              # Main application package
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py               # Application, rendering, and UI
│   ├── astronomy.py          # Sidereal time, coordinates, ephemerides
│   └── catalog.py            # Star catalog and constellation figures
├── tests/                    # Test suite (pytest)
├── install.sh                # Linux installer script
├── setup.py                  # Python package configuration
├── requirements.txt          # Required dependencies
├── README.md                 # This file
└── USAGE.md                  # Detailed usage instructions
```

## Running the Tests
```bash
pip install pytest
python -m pytest tests/
```

## License
MIT License

## Author
Starry Night Developer

## Acknowledgements
- Built with Python and Pygame
- Inspired by real astronomical data and visualization techniques