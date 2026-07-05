"""
Main application file for Starry Night - Celestial Viewer

Objects live on a celestial sphere (azimuth/altitude). A camera with
yaw/pitch/fov projects them onto the screen, so dragging the mouse truly
rotates the view and the scroll wheel zooms.
"""
import pygame
import sys
import math
import random
import datetime
from typing import List, Tuple, Optional
from dataclasses import dataclass, field

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 160, 255)
YELLOW = (255, 230, 120)
RED = (255, 90, 70)
ORANGE = (255, 165, 0)
PURPLE = (190, 120, 255)
LIGHT_BLUE = (173, 216, 230)
CYAN = (120, 230, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
HORIZON_COLOR = (70, 90, 120)
GROUND_COLOR = (18, 24, 20)
PANEL_BG = (18, 22, 40, 215)
PANEL_BORDER = (110, 130, 180)
ACCENT = (255, 210, 100)


@dataclass
class CelestialObject:
    """A celestial object positioned on the sky sphere (azimuth/altitude in radians)."""

    name: str
    azimuth: float
    altitude: float
    size: float
    color: Tuple[int, int, int]
    info: str = ""
    distance: float = 0.0  # light-years (AU for planets)
    magnitude: float = 0.0
    type: str = "star"  # "star", "planet", "galaxy"
    is_visible: bool = True
    orbital_period: float = 0.0  # days; > 0 means the object drifts along the sky
    base_azimuth: float = 0.0
    labeled: bool = False
    twinkle_phase: float = field(default_factory=lambda: random.uniform(0, 2 * math.pi))

    # Runtime state, filled in by the renderer each frame
    screen_pos: Optional[Tuple[float, float]] = None
    screen_size: float = 0.0

    def __post_init__(self):
        self.base_azimuth = self.azimuth

    def update_position(self, elapsed_days: float):
        """Advance the object along its orbit based on simulated elapsed time."""
        if self.orbital_period > 0:
            self.azimuth = (self.base_azimuth + 2 * math.pi * elapsed_days / self.orbital_period) % (2 * math.pi)

    def direction(self) -> Tuple[float, float, float]:
        """Unit direction vector: x = east, y = up, z = north."""
        cos_alt = math.cos(self.altitude)
        return (
            cos_alt * math.sin(self.azimuth),
            math.sin(self.altitude),
            cos_alt * math.cos(self.azimuth),
        )

    def is_hovered(self, mouse_pos) -> bool:
        """Check if the mouse is on or near the object's projected position."""
        if not mouse_pos or self.screen_pos is None or not self.is_visible:
            return False
        dx = mouse_pos[0] - self.screen_pos[0]
        dy = mouse_pos[1] - self.screen_pos[1]
        return math.hypot(dx, dy) <= max(8.0, self.screen_size + 4)


class TimeManager:
    """Manages simulated time playback."""

    SPEEDS = [1.0, 60.0, 3600.0, 86400.0, 604800.0, 2592000.0, 31536000.0]
    SPEED_NAMES = ["1x (real-time)", "1 min/s", "1 hour/s", "1 day/s", "1 week/s", "1 month/s", "1 year/s"]

    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.current_time = self.start_time
        self.is_playing = False
        self.current_speed_index = 3  # 1 day/s: planets visibly move

    @property
    def time_scale(self) -> float:
        return self.SPEEDS[self.current_speed_index]

    def toggle_playback(self):
        self.is_playing = not self.is_playing

    def change_speed(self, step: int):
        self.current_speed_index = max(0, min(len(self.SPEEDS) - 1, self.current_speed_index + step))

    def get_current_speed_name(self) -> str:
        return self.SPEED_NAMES[self.current_speed_index]

    def elapsed_days(self) -> float:
        return (self.current_time - self.start_time).total_seconds() / 86400.0

    def update(self, delta_time: float):
        if self.is_playing:
            self.current_time += datetime.timedelta(seconds=delta_time * self.time_scale)

    def reset_time(self):
        self.current_time = self.start_time


class Compass:
    """Compass that shows the current viewing direction (rotates with the camera)."""

    def __init__(self, radius: int):
        self.radius = radius
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)

    def draw(self, surface, center: Tuple[int, int], yaw: float, pitch: float):
        cx, cy = center
        pygame.draw.circle(surface, (*PANEL_BORDER, 0)[:3], (cx, cy), self.radius, 2)

        # Tick marks every 15 degrees, rotated so the top of the compass is
        # the direction we are looking at
        for deg in range(0, 360, 15):
            display = math.radians(deg) - yaw
            outer = (cx + self.radius * math.sin(display), cy - self.radius * math.cos(display))
            length = 10 if deg % 90 == 0 else 5
            inner = (cx + (self.radius - length) * math.sin(display),
                     cy - (self.radius - length) * math.cos(display))
            pygame.draw.line(surface, LIGHT_GRAY, inner, outer, 2 if deg % 90 == 0 else 1)

        for deg, label in ((0, "N"), (90, "E"), (180, "S"), (270, "W")):
            display = math.radians(deg) - yaw
            lx = cx + (self.radius - 22) * math.sin(display)
            ly = cy - (self.radius - 22) * math.cos(display)
            color = ACCENT if deg == 0 else WHITE
            text = self.font.render(label, True, color)
            surface.blit(text, (lx - text.get_width() // 2, ly - text.get_height() // 2))

        # Heading marker at the top + numeric heading/altitude readout
        pygame.draw.polygon(surface, ACCENT, [
            (cx, cy - self.radius - 2), (cx - 6, cy - self.radius - 12), (cx + 6, cy - self.radius - 12)])
        heading = math.degrees(yaw) % 360
        text = self.small_font.render(f"{heading:03.0f}°  alt {math.degrees(pitch):+.0f}°", True, LIGHT_GRAY)
        surface.blit(text, (cx - text.get_width() // 2, cy + self.radius + 8))


class StarryNightApp:
    """Main application class for the starry night viewer."""

    MIN_FOV = math.radians(25)
    MAX_FOV = math.radians(110)

    def __init__(self):
        pygame.init()
        self.width, self.height = 1200, 800
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Starry Night - Celestial Viewer")

        self.objects: List[CelestialObject] = []
        self.clock = pygame.time.Clock()
        self.running = True
        self.mouse_pos = None
        self.dragging = False
        self.drag_start = None
        self.drag_moved = False
        self.time_manager = TimeManager()
        self.show_controls = True
        self.show_labels = True
        self.selected_object: Optional[CelestialObject] = None
        self.hovered_object: Optional[CelestialObject] = None
        self.compass = Compass(56)

        # Camera
        self.yaw = 0.0          # heading, 0 = north, increases towards east
        self.pitch = math.radians(20)  # looking slightly up
        self.fov = math.radians(70)

        self.fonts = {size: pygame.font.SysFont(None, size) for size in (18, 20, 24, 26, 30, 48)}
        self.sky_background = None
        self.build_sky_background()
        self.create_celestial_objects()

    # ------------------------------------------------------------------ setup

    def build_sky_background(self):
        """Pre-render the vertical sky gradient once (redone on window resize)."""
        self.sky_background = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            t = y / max(1, self.height - 1)
            r = int(2 + 8 * (1 - t))
            g = int(3 + 10 * (1 - t))
            b = int(12 + 34 * (1 - t))
            pygame.draw.line(self.sky_background, (r, g, b), (0, y), (self.width, y))

    def create_celestial_objects(self):
        """Create celestial objects on the sky sphere."""
        # Background stars spread over the whole sphere
        for i in range(700):
            azimuth = random.uniform(0, 2 * math.pi)
            altitude = math.asin(random.uniform(-0.3, 1.0))  # mostly above the horizon
            size = random.uniform(0.6, 2.4)
            color = random.choice([WHITE, WHITE, WHITE, LIGHT_BLUE, YELLOW, (255, 200, 150), (255, 140, 130)])
            self.objects.append(CelestialObject(
                f"Star {i + 1}", azimuth, altitude, size, color,
                info="Background star",
                distance=round(random.uniform(4, 2000), 1),
                magnitude=round(random.uniform(2, 6.5), 2)))

        # Planets drift along an ecliptic-like band as time plays
        planets = [
            ("Mercury", ORANGE, 5, "Closest planet to the Sun", 0.39, -0.42, 88),
            ("Venus", YELLOW, 8, "Hottest planet", 0.72, -4.4, 225),
            ("Mars", RED, 6, "The Red Planet", 1.52, -1.52, 687),
            ("Jupiter", (255, 200, 140), 11, "Largest planet", 5.20, -2.20, 4333),
            ("Saturn", (235, 215, 160), 10, "Ringed planet", 9.54, -0.63, 10759),
            ("Uranus", LIGHT_BLUE, 7, "Ice giant", 19.19, -0.33, 30687),
            ("Neptune", BLUE, 7, "Windiest planet", 30.07, -0.73, 60190),
        ]
        for name, color, size, info, distance, magnitude, period in planets:
            azimuth = random.uniform(0, 2 * math.pi)
            altitude = math.radians(random.uniform(12, 40))
            self.objects.append(CelestialObject(
                name, azimuth, altitude, size, color, info, distance, magnitude,
                "planet", orbital_period=period, labeled=True))

        notable_stars = [
            ("Sirius", WHITE, 7, "Brightest star in night sky", 8.6, -1.46),
            ("Canopus", YELLOW, 6, "Second brightest star", 310, -0.74),
            ("Arcturus", ORANGE, 6, "Bright star in Bootes", 36.7, -0.05),
            ("Vega", LIGHT_BLUE, 6, "Bright star in Lyra", 25, 0.03),
            ("Capella", YELLOW, 6, "Bright star in Auriga", 42.9, 0.08),
            ("Rigel", LIGHT_BLUE, 7, "Bright star in Orion", 860, -7.0),
            ("Betelgeuse", RED, 8, "Red supergiant in Orion", 642, -0.5),
            ("Proxima Centauri", RED, 4, "Closest star to the Sun", 4.24, 11.1),
        ]
        for name, color, size, info, distance, magnitude in notable_stars:
            azimuth = random.uniform(0, 2 * math.pi)
            altitude = math.radians(random.uniform(8, 75))
            self.objects.append(CelestialObject(
                name, azimuth, altitude, size, color, info, distance, magnitude,
                "star", labeled=True))

        galaxies = [
            ("Andromeda", PURPLE, 10, "Closest large galaxy to the Milky Way", 2500000, 3.4),
            ("Whirlpool", CYAN, 8, "Spiral galaxy", 23000000, 8.4),
            ("Sombrero", YELLOW, 8, "Galaxy with a prominent dust lane", 28000000, 9.4),
        ]
        for name, color, size, info, distance, magnitude in galaxies:
            azimuth = random.uniform(0, 2 * math.pi)
            altitude = math.radians(random.uniform(20, 70))
            self.objects.append(CelestialObject(
                name, azimuth, altitude, size, color, info, distance, magnitude,
                "galaxy", labeled=True))

    # ------------------------------------------------------------- projection

    def focal_length(self) -> float:
        return (self.height / 2) / math.tan(self.fov / 2)

    def project(self, direction: Tuple[float, float, float]) -> Optional[Tuple[float, float]]:
        """Project a world direction vector to screen coordinates, or None if behind the camera."""
        x, y, z = direction
        cos_yaw, sin_yaw = math.cos(self.yaw), math.sin(self.yaw)
        x1 = x * cos_yaw - z * sin_yaw
        z1 = x * sin_yaw + z * cos_yaw
        cos_p, sin_p = math.cos(self.pitch), math.sin(self.pitch)
        y1 = y * cos_p - z1 * sin_p
        z2 = y * sin_p + z1 * cos_p
        if z2 <= 0.05:
            return None
        focal = self.focal_length()
        sx = self.width / 2 + focal * x1 / z2
        sy = self.height / 2 - focal * y1 / z2
        if -80 <= sx <= self.width + 80 and -80 <= sy <= self.height + 80:
            return (sx, sy)
        return None

    # ----------------------------------------------------------------- events

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = max(640, event.w), max(480, event.h)
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                self.build_sky_background()
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                if self.dragging:
                    dx, dy = event.rel
                    if abs(dx) + abs(dy) > 2:
                        self.drag_moved = True
                    # Grab-the-sky: the scene follows the mouse
                    sensitivity = self.fov / self.height
                    self.yaw = (self.yaw - dx * sensitivity) % (2 * math.pi)
                    self.pitch = max(math.radians(-89), min(math.radians(89),
                                                            self.pitch + dy * sensitivity))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = True
                    self.drag_moved = False
                    self.drag_start = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if not self.drag_moved:
                        self.select_object_at(event.pos)
                    self.dragging = False
            elif event.type == pygame.MOUSEWHEEL:
                zoom = math.exp(-event.y * 0.1)
                self.fov = max(self.MIN_FOV, min(self.MAX_FOV, self.fov * zoom))
            elif event.type == pygame.KEYDOWN:
                self.handle_key(event.key)

    def handle_key(self, key):
        if key == pygame.K_SPACE:
            self.time_manager.toggle_playback()
        elif key == pygame.K_r:
            self.time_manager.reset_time()
            for obj in self.objects:
                obj.update_position(0.0)
        elif key == pygame.K_c:
            self.show_controls = not self.show_controls
        elif key == pygame.K_l:
            self.show_labels = not self.show_labels
        elif key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self.time_manager.change_speed(1)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.time_manager.change_speed(-1)
        elif key == pygame.K_t:
            if self.selected_object:
                self.selected_object.is_visible = not self.selected_object.is_visible
        elif key == pygame.K_ESCAPE:
            if self.selected_object:
                self.selected_object = None
            else:
                self.running = False

    def select_object_at(self, pos):
        """Select the labeled object closest to the click, if any is near."""
        best, best_dist = None, 18.0
        for obj in self.objects:
            if obj.screen_pos is None or not obj.is_visible:
                continue
            dist = math.hypot(pos[0] - obj.screen_pos[0], pos[1] - obj.screen_pos[1])
            dist -= obj.screen_size  # favor clicking anywhere inside big objects
            if dist < best_dist:
                best, best_dist = obj, dist
        self.selected_object = best

    # ----------------------------------------------------------------- update

    def update(self):
        delta_time = self.clock.get_time() / 1000.0
        # Keyboard rotation (arrow keys), scaled with zoom level
        keys = pygame.key.get_pressed()
        rot_speed = self.fov * delta_time
        if keys[pygame.K_LEFT]:
            self.yaw = (self.yaw - rot_speed) % (2 * math.pi)
        if keys[pygame.K_RIGHT]:
            self.yaw = (self.yaw + rot_speed) % (2 * math.pi)
        if keys[pygame.K_UP]:
            self.pitch = min(math.radians(89), self.pitch + rot_speed)
        if keys[pygame.K_DOWN]:
            self.pitch = max(math.radians(-89), self.pitch - rot_speed)

        self.time_manager.update(delta_time)
        elapsed = self.time_manager.elapsed_days()
        for obj in self.objects:
            if obj.orbital_period > 0:
                obj.update_position(elapsed)

    # ------------------------------------------------------------------- draw

    def draw(self):
        self.screen.blit(self.sky_background, (0, 0))
        self.draw_horizon()
        self.draw_objects()
        self.compass.draw(self.screen, (self.width - 90, 96), self.yaw, self.pitch)
        self.draw_hud()
        if self.show_controls:
            self.draw_controls()
        if self.selected_object:
            self.draw_info_panel(self.selected_object)
        pygame.display.flip()

    def draw_horizon(self):
        """Draw the horizon line with cardinal direction markers."""
        points = []
        for deg in range(0, 361, 3):
            direction = (math.sin(math.radians(deg)), 0.0, math.cos(math.radians(deg)))
            pos = self.project(direction)
            points.append(pos)
        # Draw as connected segments, skipping gaps that leave the screen
        segment = []
        for pos in points + [None]:
            if pos:
                segment.append(pos)
            else:
                if len(segment) >= 2:
                    pygame.draw.lines(self.screen, HORIZON_COLOR, False, segment, 2)
                segment = []
        # Cardinal labels on the horizon
        font = self.fonts[26]
        for deg, label in ((0, "N"), (90, "E"), (180, "S"), (270, "W")):
            direction = (math.sin(math.radians(deg)), 0.0, math.cos(math.radians(deg)))
            pos = self.project(direction)
            if pos:
                text = font.render(label, True, ACCENT)
                self.screen.blit(text, (pos[0] - text.get_width() // 2, pos[1] + 8))

    def draw_objects(self):
        ticks = pygame.time.get_ticks() / 1000.0
        zoom_scale = math.sqrt(self.focal_length() / ((self.height / 2) / math.tan(math.radians(35))))
        self.hovered_object = None
        label_font = self.fonts[18]

        for obj in self.objects:
            obj.screen_pos = None
            if not obj.is_visible:
                continue
            pos = self.project(obj.direction())
            if pos is None:
                continue
            obj.screen_pos = pos
            obj.screen_size = max(1.0, obj.size * zoom_scale)

            # Subtle time-based twinkle for small background stars
            color = obj.color
            if obj.type == "star" and not obj.labeled:
                factor = 0.8 + 0.2 * math.sin(ticks * 2.5 + obj.twinkle_phase)
                color = tuple(int(c * factor) for c in obj.color)

            x, y = int(pos[0]), int(pos[1])
            radius = int(obj.screen_size)
            if obj.labeled and radius >= 3:
                glow_radius = radius * 2
                glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*obj.color, 60), (glow_radius, glow_radius), glow_radius)
                self.screen.blit(glow, (x - glow_radius, y - glow_radius))
            pygame.draw.circle(self.screen, color, (x, y), max(1, radius))

            if obj is self.selected_object:
                pygame.draw.circle(self.screen, ACCENT, (x, y), radius + 8, 2)
            if self.show_labels and obj.labeled:
                text = label_font.render(obj.name, True, LIGHT_GRAY)
                self.screen.blit(text, (x - text.get_width() // 2, y + radius + 4))

            if self.hovered_object is None and obj.is_hovered(self.mouse_pos):
                self.hovered_object = obj

        if self.hovered_object and self.hovered_object is not self.selected_object:
            self.draw_tooltip(self.hovered_object)

    def draw_tooltip(self, obj: CelestialObject):
        x, y = obj.screen_pos
        name_text = self.fonts[24].render(obj.name, True, WHITE)
        unit = "AU" if obj.type == "planet" else "ly"
        info_text = self.fonts[18].render(
            f"{obj.type.capitalize()} | {obj.distance:g} {unit} | mag {obj.magnitude:g}", True, LIGHT_BLUE)
        w = max(name_text.get_width(), info_text.get_width()) + 16
        h = name_text.get_height() + info_text.get_height() + 14
        tx = min(max(8, x - w / 2), self.width - w - 8)
        ty = max(8, y - obj.screen_size - h - 12)
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill(PANEL_BG)
        self.screen.blit(panel, (tx, ty))
        self.screen.blit(name_text, (tx + 8, ty + 5))
        self.screen.blit(info_text, (tx + 8, ty + 8 + name_text.get_height()))

    def draw_hud(self):
        """Top bar with time, speed and play state."""
        bar = pygame.Surface((self.width, 42), pygame.SRCALPHA)
        bar.fill((10, 12, 28, 200))
        self.screen.blit(bar, (0, 0))

        state = "PLAYING" if self.time_manager.is_playing else "PAUSED  (SPACE to play)"
        state_color = (140, 255, 140) if self.time_manager.is_playing else ACCENT
        time_str = self.time_manager.current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.screen.blit(self.fonts[24].render(f"Time: {time_str}", True, WHITE), (16, 12))
        self.screen.blit(self.fonts[24].render(
            f"Speed: {self.time_manager.get_current_speed_name()}", True, LIGHT_GRAY), (300, 12))
        self.screen.blit(self.fonts[24].render(state, True, state_color), (560, 12))

        title = self.fonts[30].render("Starry Night", True, WHITE)
        self.screen.blit(title, (self.width - title.get_width() - 200, 10))

        hint = self.fonts[20].render(
            "Drag or arrow keys to look around | scroll to zoom | click an object for details | C for help",
            True, GRAY)
        self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 26))

    def draw_controls(self):
        controls = [
            ("Drag / Arrows", "look around"),
            ("Scroll", "zoom in/out"),
            ("Click", "select object"),
            ("SPACE", "play / pause time"),
            ("+ / -", "time speed"),
            ("R", "reset time"),
            ("T", "hide/show selection"),
            ("L", "toggle labels"),
            ("C", "toggle this panel"),
            ("ESC", "deselect / quit"),
        ]
        width, row_h = 300, 22
        height = 46 + len(controls) * row_h
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill(PANEL_BG)
        pygame.draw.rect(panel, PANEL_BORDER, (0, 0, width, height), 1)
        panel.blit(self.fonts[26].render("Controls", True, WHITE), (12, 10))
        for i, (key, action) in enumerate(controls):
            y = 42 + i * row_h
            panel.blit(self.fonts[20].render(key, True, ACCENT), (12, y))
            panel.blit(self.fonts[20].render(action, True, LIGHT_GRAY), (140, y))
        self.screen.blit(panel, (16, 56))

    def draw_info_panel(self, obj: CelestialObject):
        unit = "AU" if obj.type == "planet" else "ly"
        lines = [
            (obj.type.capitalize(), LIGHT_BLUE),
            (f"Distance: {obj.distance:g} {unit}", LIGHT_GRAY),
            (f"Magnitude: {obj.magnitude:g}", LIGHT_GRAY),
        ]
        if obj.orbital_period > 0:
            lines.append((f"Orbital period: {obj.orbital_period:g} days", LIGHT_GRAY))
        if obj.info:
            lines.append((obj.info, WHITE))
        lines.append(("T: hide/show   ESC: deselect", GRAY))

        width, row_h = 340, 22
        height = 48 + len(lines) * row_h
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill(PANEL_BG)
        pygame.draw.rect(panel, PANEL_BORDER, (0, 0, width, height), 1)
        panel.blit(self.fonts[26].render(obj.name, True, ACCENT), (12, 10))
        for i, (line, color) in enumerate(lines):
            panel.blit(self.fonts[20].render(line, True, color), (12, 42 + i * row_h))
        self.screen.blit(panel, (self.width - width - 16, self.height - height - 40))

    # -------------------------------------------------------------------- run

    def run(self):
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
