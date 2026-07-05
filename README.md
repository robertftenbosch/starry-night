# Starry Night - Celestial Viewer

A desktop application that displays celestial objects in a dome-like starry night visualization with hover information.

## Features
- Dome-like visualization of celestial objects
- Display of object names and additional information on hover
- Linux installer support
- Python-based with Pygame visualization

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

## Development
- Uses Python with Pygame for visualization
- Linux installer support via setuptools
```