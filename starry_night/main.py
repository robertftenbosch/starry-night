"""
Main application file for Starry Night - Celestial Viewer
"""
import pygame
import sys
import math
import random
from typing import List, Tuple

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
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

class CelestialObject:
    """Represents a celestial object with position and properties"""

    def __init__(self, name: str, x: float, y: float, size: float, color: Tuple[int, int, int],
                 info: str = "", distance: float = 0.0, magnitude: float = 0.0):
        self.name = name
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.info = info
        self.distance = distance  # in light years
        self.magnitude = magnitude  # brightness

    def draw(self, surface, mouse_pos=None):
        """Draw the celestial object"""
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

class StarryNightApp:
    """Main application class for the starry night viewer"""

    def __init__(self):
        self.objects: List[CelestialObject] = []
        self.clock = pygame.time.Clock()
        self.running = True
        self.mouse_pos = None
        self.create_celestial_objects()

    def create_celestial_objects(self):
        """Create celestial objects for the visualization"""
        # Create some stars
        for _ in range(200):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.uniform(0.5, 2.5)
            # Create a range of star colors (white, blue, yellow, red)
            color = random.choice([WHITE, BLUE, YELLOW, (255, 200, 150)])
            name = f"Star {random.randint(1, 1000)}"
            info = f"Stellar object with size {size:.1f}"
            distance = random.uniform(1, 1000)
            magnitude = random.uniform(-2, 10)
            self.objects.append(CelestialObject(name, x, y, size, color, info, distance, magnitude))

        # Add some planets
        planets = [
            ("Mercury", ORANGE, 10, "Closest planet to the Sun", 0.39, -0.42),
            ("Venus", YELLOW, 12, "Hottest planet", 0.72, -4.4),
            ("Earth", BLUE, 12, "Our home planet", 1.0, -2.63),
            ("Mars", RED, 11, "The Red Planet", 1.52, -1.52),
            ("Jupiter", ORANGE, 20, "Largest planet", 5.20, -2.20),
            ("Saturn", YELLOW, 18, "Ringed planet", 9.54, -0.63),
            ("Uranus", LIGHT_BLUE, 15, "Ice giant", 19.19, -0.33),
            ("Neptune", BLUE, 15, "Windiest planet", 30.07, -0.73)
        ]

        for name, color, size, info, distance, magnitude in planets:
            # Position planets in a circular pattern
            angle = random.uniform(0, 2 * math.pi)
            radius = random.randint(300, 450)
            x = WIDTH // 2 + radius * math.cos(angle)
            y = HEIGHT // 2 + radius * math.sin(angle)
            self.objects.append(CelestialObject(name, x, y, size, color, info, distance, magnitude))

        # Add some notable stars
        notable_stars = [
            ("Sirius", WHITE, 15, "Brightest star in night sky", 8.6, -1.46),
            ("Canopus", YELLOW, 14, "Second brightest star", 310, -0.74),
            ("Arcturus", ORANGE, 13, "Brightest star in Bootes", 36.7, -0.05),
            ("Vega", BLUE, 12, "Bright star in Lyra", 25, 0.03),
            ("Capella", YELLOW, 13, "Bright star in Auriga", 42.9, 0.08)
        ]

        for name, color, size, info, distance, magnitude in notable_stars:
            angle = random.uniform(0, 2 * math.pi)
            radius = random.randint(200, 300)
            x = WIDTH // 2 + radius * math.cos(angle)
            y = HEIGHT // 2 + radius * math.sin(angle)
            self.objects.append(CelestialObject(name, x, y, size, color, info, distance, magnitude))

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

    def update(self):
        """Update the application state"""
        pass

    def draw(self):
        """Draw the entire scene"""
        screen.fill(BLACK)

        # Draw dome-like effect
        self.draw_dome()

        # Draw celestial objects
        for obj in self.objects:
            obj.draw(screen, self.mouse_pos)

        # Draw title
        font = pygame.font.SysFont(None, 48)
        title = font.render("Starry Night - Celestial Viewer", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        # Draw instructions
        font = pygame.font.SysFont(None, 24)
        instructions = font.render("Hover over objects to see information", True, WHITE)
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