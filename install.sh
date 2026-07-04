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