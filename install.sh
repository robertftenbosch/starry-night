#!/bin/bash

# Starry Night - Linux Installer Script
# This script installs the Starry Night celestial viewer application

set -e  # Exit on any error

echo "Installing Starry Night - Celestial Viewer"
echo "=========================================="

# Check if we're on a Linux system
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Error: This installer is only for Linux systems."
    exit 1
fi

# Check if python3 and pip are available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "Error: pip is not installed."
    exit 1
fi

# Try to detect the package manager and install SDL dependencies
echo "Checking for required system dependencies..."
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    echo "Installing SDL development libraries for Debian/Ubuntu..."
    sudo apt-get update
    sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
elif command -v yum &> /dev/null; then
    # Red Hat/CentOS/Fedora
    echo "Installing SDL development libraries for Red Hat/CentOS/Fedora..."
    sudo yum install -y SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel
elif command -v dnf &> /dev/null; then
    # Fedora
    echo "Installing SDL development libraries for Fedora..."
    sudo dnf install -y SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel
else
    echo "Warning: Could not detect package manager. Please install SDL2 development libraries manually:"
    echo "  Debian/Ubuntu: sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev"
    echo "  Red Hat/CentOS: sudo yum install SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel"
    echo "  Fedora: sudo dnf install SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel"
fi

# Create installation directory
INSTALL_DIR="$HOME/.local/share/starry-night"
mkdir -p "$INSTALL_DIR"

# Copy application files
echo "Copying application files..."
cp -r ./* "$INSTALL_DIR/"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source "$INSTALL_DIR/venv/bin/activate"
pip install --upgrade pip
pip install pygame requests numpy

# Install the application in development mode
pip install -e "$INSTALL_DIR"

# Create desktop entry
echo "Creating desktop entry..."
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/starry-night.desktop" << EOF
[Desktop Entry]
Name=Starry Night
Comment=Celestial Viewer Application
Exec=sh -c 'cd $INSTALL_DIR && source venv/bin/activate && python -m starry_night'
Icon=
Terminal=true
Type=Application
Categories=Application;Education;
EOF

# Create a launcher script
echo "Creating launcher script..."
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/starry-night" << EOF
#!/bin/bash
cd $INSTALL_DIR
source venv/bin/activate
python -m starry_night
EOF

chmod +x "$HOME/.local/bin/starry-night"

echo "Installation complete!"
echo ""
echo "To run the application:"
echo "  starry-night"
echo ""
echo "The application has been installed in: $INSTALL_DIR"
echo "Virtual environment: $INSTALL_DIR/venv"