# Starry Night - Celestial Viewer Usage Guide

## Overview
Starry Night is a desktop application that displays celestial objects in a dome-like starry night visualization. You can hover over objects to see additional information about them.

## Features
- Dome-like visualization of the night sky
- Display of celestial object names and information on hover
- Support for stars, planets, and notable celestial objects
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

1. The application opens in a window showing a dome-like visualization of the night sky
2. Hover your mouse over any celestial object (star, planet, etc.)
3. Information about the object will appear including:
   - Object name
   - Distance from Earth (in light years)
   - Magnitude (brightness)
4. Close the window by clicking the close button or pressing Ctrl+C in the terminal

## Customization

The application currently comes with a predefined set of celestial objects. To customize:
1. Modify `starry_night/main.py` 
2. Add more objects to the `create_celestial_objects()` method
3. Reinstall the application

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