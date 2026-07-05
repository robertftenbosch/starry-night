"""
Main application file for Starry Night - Celestial Viewer
"""
import pygame
import sys
import math
import random
import datetime
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starry Night - Celestial Viewer")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
LIGHT_BLUE = (173, 216, 230)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

@dataclass
class CelestialObject:
    """Represents a celestial object with position and properties"""

    name: str
    x: float
    y: float
    size: float
    color: Tuple[int, int, int]
    info: str = ""
    distance: float = 0.0
    magnitude: float = 0.0
    type: str = "star"  # "star", "planet", "galaxy", "comet", etc.
    is_visible: bool = True
    orbital_radius: float = 0.0
    orbital_period: float = 0.0  # in days
    angle: float = 0.0  # current angle in orbit
    epoch: datetime.datetime = None  # reference time for orbital calculations

    def __post_init__(self):
        if self.epoch is None:
            self.epoch = datetime.datetime.now()

    def update_position(self, time_delta: float):
        """Update object position based on orbital mechanics"""
        if self.orbital_period > 0:
            # Update angle based on orbital period and time delta
            self.angle += (time_delta / self.orbital_period) * 0.01  # Adjust speed factor as needed

    def draw(self, surface, mouse_pos=None, time_scale=1.0):
        """Draw the celestial object"""
        if not self.is_visible:
            return

        # Draw glow effect
        glow_radius = int(self.size * 1.5)
        if glow_radius > 0:
            s = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, 100), (glow_radius, glow_radius), glow_radius)
            surface.blit(s, (self.x - glow_radius, self.y - glow_radius))

        # Draw the object
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

        # Draw name if mouse is hovering
        if mouse_pos and self.is_hovered(mouse_pos):
            font = pygame.font.SysFont(None, 24)
            text = font.render(self.name, True, WHITE)
            surface.blit(text, (self.x - text.get_width() // 2, self.y - self.size - 30))

            # Draw additional info
            info_font = pygame.font.SysFont(None, 18)
            info_text = info_font.render(f"Distance: {self.distance} ly | Magnitude: {self.magnitude}", True, LIGHT_BLUE)
            surface.blit(info_text, (self.x - info_text.get_width() // 2, self.y - self.size - 55))

    def is_hovered(self, mouse_pos):
        """Check if mouse is hovering over the object"""
        if mouse_pos:
            distance = math.sqrt((mouse_pos[0] - self.x)**2 + (mouse_pos[1] - self.y)**2)
            return distance <= self.size
        return False

class TimeManager:
    """Manages time playback for the celestial viewer"""

    def __init__(self):
        self.current_time = datetime.datetime.now()
        self.start_time = self.current_time
        self.end_time = self.current_time + datetime.timedelta(days=365)  # One year ahead
        self.is_playing = False
        self.time_scale = 1.0  # 1 second real time = 1 second simulation time
        self.speeds = [0.1, 0.5, 1.0, 5.0, 10.0, 60.0, 3600.0, 86400.0, 2592000.0, 31536000.0]  # seconds: 1s, 5s, 10s, 1m, 10m, 1h, 1d, 1w, 1mo, 1y
        self.speed_names = ["1s", "5s", "10s", "1m", "10m", "1h", "1d", "1w", "1mo", "1y"]
        self.current_speed_index = 2  # Start with 10s per second

    def toggle_playback(self):
        """Toggle time playback"""
        self.is_playing = not self.is_playing

    def set_time_scale(self, scale_index: int):
        """Set time scale by index"""
        if 0 <= scale_index < len(self.speeds):
            self.current_speed_index = scale_index
            self.time_scale = self.speeds[scale_index]

    def get_current_speed_name(self):
        """Get the name of the current time speed"""
        return self.speed_names[self.current_speed_index]

    def update(self, delta_time: float):
        """Update time based on playback state"""
        if self.is_playing:
            # Calculate time increment based on time scale
            time_increment = delta_time * self.time_scale
            self.current_time += datetime.timedelta(seconds=time_increment)

    def reset_time(self):
        """Reset to start time"""
        self.current_time = self.start_time

    def set_time_range(self, start_time: datetime.datetime, end_time: datetime.datetime):
        """Set time range for playback"""
        self.start_time = start_time
        self.end_time = end_time
        self.current_time = start_time

class Compass:
    """Compass system for celestial orientation"""

    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.directions = {
            0: "N",  # North
            90: "E", # East
            180: "S", # South
            270: "W" # West
        }

    def draw(self, surface):
        """Draw the compass"""
        # Draw compass circle
        pygame.draw.circle(surface, WHITE, (self.center_x, self.center_y), self.radius, 2)

        # Draw direction markers
        for angle in range(0, 360, 15):  # Every 15 degrees
            rad_angle = math.radians(angle)
            x1 = self.center_x + (self.radius - 10) * math.cos(rad_angle)
            y1 = self.center_y + (self.radius - 10) * math.sin(rad_angle)
            x2 = self.center_x + self.radius * math.cos(rad_angle)
            y2 = self.center_y + self.radius * math.sin(rad_angle)

            # Draw marker line
            pygame.draw.line(surface, WHITE, (x1, y1), (x2, y2), 2)

            # Draw direction labels
            if angle in self.directions:
                label_x = self.center_x + (self.radius + 20) * math.cos(rad_angle)
                label_y = self.center_y + (self.radius + 20) * math.sin(rad_angle)
                font = pygame.font.SysFont(None, 24)
                text = font.render(self.directions[angle], True, WHITE)
                surface.blit(text, (label_x - text.get_width() // 2, label_y - text.get_height() // 2))

        # Draw center point
        pygame.draw.circle(surface, WHITE, (self.center_x, self.center_y), 5)

        # Draw north indicator
        font = pygame.font.SysFont(None, 24)
        north_text = font.render("N", True, WHITE)
        surface.blit(north_text, (self.center_x - north_text.get_width() // 2, self.center_y - self.radius - 30))

class StarryNightApp:
    """Main application class for the starry night viewer"""

    def __init__(self):
        self.objects: List[CelestialObject] = []
        self.clock = pygame.time.Clock()
        self.running = True
        self.mouse_pos = None
        self.time_manager = TimeManager()
        self.show_controls = True
        self.selected_object = None
        self.object_visibility = {}
        self.compass = Compass(WIDTH - 100, 100, 60)
        self.create_celestial_objects()
        self.setup_object_visibility()

    def create_celestial_objects(self):
        """Create celestial objects for the visualization"""
        # Create stars
        for _ in range(500):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.uniform(0.5, 3.0)
            # Create a range of star colors (white, blue, yellow, red)
            color = random.choice([WHITE, BLUE, YELLOW, (255, 200, 150), (255, 100, 100)])
            name = f"Star {random.randint(1, 1000)}"
            info = f"Stellar object with size {size:.1f}"
            distance = random.uniform(1, 1000)
            magnitude = random.uniform(-2, 10)
            self.objects.append(CelestialObject(name, x, y, size, color, info, distance, magnitude, "star"))

        # Add planets with orbital mechanics
        planets = [
            ("Mercury", ORANGE, 8, "Closest planet to the Sun", 0.39, -0.42, 88, 0),
            ("Venus", YELLOW, 10, "Hottest planet", 0.72, -4.4, 225, 0),
            ("Earth", BLUE, 10, "Our home planet", 1.0, -2.63, 365, 0),
            ("Mars", RED, 9, "The Red Planet", 1.52, -1.52, 687, 0),
            ("Jupiter", ORANGE, 20, "Largest planet", 5.20, -2.20, 4333, 0),
            ("Saturn", YELLOW, 18, "Ringed planet", 9.54, -0.63, 10759, 0),
            ("Uranus", LIGHT_BLUE, 15, "Ice giant", 19.19, -0.33, 30687, 0),
            ("Neptune", BLUE, 15, "Windiest planet", 30.07, -0.73, 60190, 0)
        ]

        for name, color, size, info, distance, magnitude, orbital_period, angle in planets:
            # Position planets in a circular pattern with some randomness
            angle = random.uniform(0, 2 * math.pi)
            radius = random.randint(300, 500)
            x = WIDTH // 2 + radius * math.cos(angle)
            y = HEIGHT // 2 + radius * math.sin(angle)
            obj = CelestialObject(name, x, y, size, color, info, distance, magnitude, "planet", True, radius, orbital_period, angle)
            self.objects.append(obj)

        # Add some notable stars
        notable_stars = [
            ("Sirius", WHITE, 15, "Brightest star in night sky", 8.6, -1.46, 0, 0),
            ("Canopus", YELLOW, 14, "Second brightest star", 310, -0.74, 0, 0),
            ("Arcturus", ORANGE, 13, "Bright star in Bootes", 36.7, -0.05, 0, 0),
            ("Vega", BLUE, 12, "Bright star in Lyra", 25, 0.03, 0, 0),
            ("Capella", YELLOW, 13, "Bright star in Auriga", 42.9, 0.08, 0, 0),
            ("Rigel", BLUE, 16, "Bright star in Orion", 860, -7.0, 0, 0),
            ("Betelgeuse", RED, 18, "Red supergiant in Orion", 642, -0.5, 0, 0),
            ("Proxima Centauri", RED, 6, "Closest star to Sun", 4.24, 11.1, 0, 0)
        ]

        for name, color, size, info, distance, magnitude, orbital_period, angle in notable_stars:
            angle = random.uniform(0, 2 * math.pi)
            radius = random.randint(200, 400)
            x = WIDTH // 2 + radius * math.cos(angle)
            y = HEIGHT // 2 + radius * math.sin(angle)
            self.objects.append(CelestialObject(name, x, y, size, color, info, distance, magnitude, "star", True, radius, orbital_period, angle))

        # Add some galaxies
        galaxies = [
            ("Andromeda", PURPLE, 25, "Closest galaxy to Milky Way", 2500000, -2.0, 0, 0),
            ("Whirlpool", CYAN, 20, "Spiral galaxy", 23000000, -8.4, 0, 0),
            ("Sombrero", YELLOW, 18, "Galaxy with prominent dust lane", 28000000, -9.4, 0, 0)
        ]

        for name, color, size, info, distance, magnitude, orbital_period, angle in galaxies:
            angle = random.uniform(0, 2 * math.pi)
            radius = random.randint(400, 600)
            x = WIDTH // 2 + radius * math.cos(angle)
            y = HEIGHT // 2 + radius * math.sin(angle)
            self.objects.append(CelestialObject(name, x, y, size, color, info, distance, magnitude, "galaxy", True, radius, orbital_period, angle))

    def setup_object_visibility(self):
        """Set up initial visibility for objects"""
        for obj in self.objects:
            self.object_visibility[obj.name] = obj.is_visible

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if clicked on an object
                    for obj in reversed(self.objects):  # Check from front to back
                        if obj.is_hovered(self.mouse_pos):
                            self.selected_object = obj
                            break
                    else:
                        self.selected_object = None
                elif event.button == 4:  # Scroll up
                    # Zoom in
                    pass
                elif event.button == 5:  # Scroll down
                    # Zoom out
                    pass
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.time_manager.toggle_playback()
                elif event.key == pygame.K_r:
                    self.time_manager.reset_time()
                elif event.key == pygame.K_c:
                    self.show_controls = not self.show_controls
                elif event.key == pygame.K_UP:
                    # Speed up time
                    if self.time_manager.current_speed_index < len(self.time_manager.speeds) - 1:
                        self.time_manager.set_time_scale(self.time_manager.current_speed_index + 1)
                elif event.key == pygame.K_DOWN:
                    # Slow down time
                    if self.time_manager.current_speed_index > 0:
                        self.time_manager.set_time_scale(self.time_manager.current_speed_index - 1)
                elif event.key == pygame.K_t:
                    # Toggle object visibility
                    if self.selected_object:
                        self.selected_object.is_visible = not self.selected_object.is_visible
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        """Update the application state"""
        # Update time
        delta_time = self.clock.get_time() / 1000.0  # Convert to seconds
        self.time_manager.update(delta_time)

        # Update orbital positions
        for obj in self.objects:
            if obj.orbital_period > 0:
                obj.update_position(delta_time)

    def draw(self):
        """Draw the entire scene"""
        screen.fill(BLACK)

        # Draw dome-like effect
        self.draw_dome()

        # Draw celestial objects
        for obj in self.objects:
            obj.draw(screen, self.mouse_pos, self.time_manager.time_scale)

        # Draw compass
        self.compass.draw(screen)

        # Draw title
        font = pygame.font.SysFont(None, 48)
        title = font.render("Starry Night - Celestial Viewer", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        # Draw time information
        time_str = self.time_manager.current_time.strftime("%Y-%m-%d %H:%M:%S")
        font = pygame.font.SysFont(None, 24)
        time_text = font.render(f"Time: {time_str} | Speed: {self.time_manager.get_current_speed_name()}", True, WHITE)
        screen.blit(time_text, (20, 20))

        # Draw controls if visible
        if self.show_controls:
            self.draw_controls()

        # Draw instructions
        font = pygame.font.SysFont(None, 24)
        instructions = font.render("Controls: SPACE (play/pause), R (reset), UP/DOWN (speed), C (toggle controls), T (toggle object), ESC (quit)", True, WHITE)
        screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 40))

        pygame.display.flip()

    def draw_dome(self):
        """Draw a dome-like effect for the sky"""
        # Draw gradient background
        for y in range(HEIGHT // 2):
            # Create a gradient from dark blue to black
            intensity = max(0, 255 - (y // 3))
            color = (0, 0, intensity)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

    def draw_controls(self):
        """Draw control panel"""
        # Draw control panel background
        panel_width = 300
        panel_height = 200
        panel_x = 20
        panel_y = 60

        pygame.draw.rect(screen, (30, 30, 50, 180), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2)

        font = pygame.font.SysFont(None, 24)
        title = font.render("Controls", True, WHITE)
        screen.blit(title, (panel_x + 10, panel_y + 10))

        # Draw playback controls
        font_small = pygame.font.SysFont(None, 20)
        controls = [
            "SPACE: Play/Pause",
            "R: Reset Time",
            "UP/DOWN: Speed",
            "C: Toggle Controls",
            "T: Toggle Object",
            "ESC: Quit"
        ]

        for i, control in enumerate(controls):
            text = font_small.render(control, True, WHITE)
            screen.blit(text, (panel_x + 10, panel_y + 40 + i * 20))

    def run(self):
        """Main application loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

def main():
    """Main entry point"""
    app = StarryNightApp()
    app.run()

if __name__ == "__main__":
    main()