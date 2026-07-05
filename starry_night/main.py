"""
Main application file for Starry Night - Celestial Viewer

A real-sky planetarium: stars come from a catalog with true J2000
coordinates, the whole sky rotates with (simulated) time as the Earth
turns, and the Sun, Moon, and planets follow real ephemerides. A camera
with yaw/pitch/fov projects the sky onto the screen, so dragging the
mouse rotates the view and the scroll wheel zooms.
"""
import argparse
import datetime
import math
import random
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import pygame

from . import astronomy
from .catalog import CONSTELLATION_LINES, GALAXIES, STARS

# Colors
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
HORIZON_COLOR = (90, 105, 130)
CONSTELLATION_COLOR = (70, 95, 140)
PANEL_BG = (18, 22, 40, 215)
PANEL_BORDER = (110, 130, 180)
ACCENT = (255, 210, 100)

STAR_COLORS = {
    "white": (255, 255, 255),
    "blue": (170, 195, 255),
    "yellow": (255, 235, 170),
    "orange": (255, 190, 120),
    "red": (255, 150, 120),
}
PLANET_COLORS = {
    "Mercury": (200, 180, 160),
    "Venus": (255, 240, 200),
    "Mars": (255, 120, 80),
    "Jupiter": (255, 200, 140),
    "Saturn": (235, 215, 160),
    "Uranus": (170, 220, 230),
    "Neptune": (130, 170, 255),
}
# Rough visual magnitudes, used for brightness/visibility only
PLANET_MAGNITUDES = {
    "Mercury": 0.0, "Venus": -4.1, "Mars": 0.7, "Jupiter": -2.2,
    "Saturn": 0.6, "Uranus": 5.7, "Neptune": 7.9,
}

# (sun altitude deg, zenith color, horizon color) — lerped for the sky gradient
SKY_KEYFRAMES = [
    (-90, (2, 3, 12), (10, 13, 46)),
    (-18, (2, 3, 12), (10, 13, 46)),
    (-9, (6, 9, 28), (32, 36, 68)),
    (-4, (12, 20, 52), (105, 72, 62)),
    (0, (35, 60, 110), (225, 132, 72)),
    (6, (70, 115, 195), (215, 190, 160)),
    (15, (95, 155, 235), (175, 205, 240)),
    (90, (95, 155, 235), (175, 205, 240)),
]

DEFAULT_LATITUDE = 52.37   # Amsterdam
DEFAULT_LONGITUDE = 4.90


def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def sky_palette(sun_alt_deg: float):
    """Zenith and horizon colors for a given sun altitude."""
    for (a1, z1, h1), (a2, z2, h2) in zip(SKY_KEYFRAMES, SKY_KEYFRAMES[1:]):
        if a1 <= sun_alt_deg <= a2:
            t = (sun_alt_deg - a1) / (a2 - a1)
            return lerp_color(z1, z2, t), lerp_color(h1, h2, t)
    return SKY_KEYFRAMES[-1][1], SKY_KEYFRAMES[-1][2]


def limiting_magnitude(sun_alt_deg: float) -> float:
    """Faintest visible magnitude given the sun's altitude (twilight fade)."""
    if sun_alt_deg <= -18:
        return 8.0
    if sun_alt_deg <= 0:
        return 8.0 + (sun_alt_deg + 18) / 18 * (-1.5 - 8.0)
    return max(-5.0, -1.5 + sun_alt_deg * -0.5)


@dataclass
class CelestialObject:
    """An object on the celestial sphere, positioned by RA/Dec (radians)."""

    name: str
    ra: float
    dec: float
    mag: float
    color: Tuple[int, int, int]
    type: str = "star"  # "star", "planet", "galaxy", "sun", "moon"
    info: str = ""
    distance_ly: float = 0.0
    distance_au: float = 0.0
    distance_km: float = 0.0
    constellation: str = ""
    labeled: bool = False
    is_visible: bool = True
    twinkle_phase: float = field(default_factory=lambda: random.uniform(0, 2 * math.pi))

    # Runtime state, filled in each frame
    azimuth: float = 0.0
    altitude: float = -1.0
    screen_pos: Optional[Tuple[float, float]] = None  # clipped to (near) screen
    view_pos: Optional[Tuple[float, float]] = None    # unclipped, for lines
    screen_size: float = 0.0

    def __post_init__(self):
        self._update_trig()

    def _update_trig(self):
        self.sin_dec = math.sin(self.dec)
        self.cos_dec = math.cos(self.dec)

    def set_equatorial(self, ra: float, dec: float):
        """Move the object (used for the Sun, Moon, and planets)."""
        self.ra, self.dec = ra, dec
        self._update_trig()

    def update_horizontal(self, lst: float, sin_lat: float, cos_lat: float):
        self.azimuth, self.altitude = astronomy.equatorial_to_horizontal(
            self.sin_dec, self.cos_dec, self.ra, lst, sin_lat, cos_lat)

    def direction(self) -> Tuple[float, float, float]:
        """Unit direction vector: x = east, y = up, z = north."""
        cos_alt = math.cos(self.altitude)
        return (
            cos_alt * math.sin(self.azimuth),
            math.sin(self.altitude),
            cos_alt * math.cos(self.azimuth),
        )

    def distance_text(self) -> Optional[str]:
        if self.type == "sun" or self.type == "planet":
            return f"Distance: {self.distance_au:.2f} AU"
        if self.type == "moon":
            return f"Distance: {self.distance_km:,.0f} km"
        if self.distance_ly >= 1e6:
            return f"Distance: {self.distance_ly / 1e6:.1f} million ly"
        if self.distance_ly > 0:
            return f"Distance: {self.distance_ly:g} ly"
        return None

    def is_hovered(self, mouse_pos) -> bool:
        if not mouse_pos or self.screen_pos is None or not self.is_visible:
            return False
        dx = mouse_pos[0] - self.screen_pos[0]
        dy = mouse_pos[1] - self.screen_pos[1]
        return math.hypot(dx, dy) <= max(8.0, self.screen_size + 4)


class TimeManager:
    """Manages simulated time playback. Internally UTC; displayed as local time."""

    SPEEDS = [1.0, 60.0, 600.0, 3600.0, 86400.0, 604800.0, 2592000.0]
    SPEED_NAMES = ["1x (real-time)", "1 min/s", "10 min/s", "1 hour/s",
                   "1 day/s", "1 week/s", "1 month/s"]

    def __init__(self):
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.current_time = self.start_time
        self.is_playing = False
        self.current_speed_index = 2  # 10 min/s: the sky visibly rotates

    @property
    def time_scale(self) -> float:
        return self.SPEEDS[self.current_speed_index]

    def toggle_playback(self):
        self.is_playing = not self.is_playing

    def change_speed(self, step: int):
        self.current_speed_index = max(0, min(len(self.SPEEDS) - 1, self.current_speed_index + step))

    def get_current_speed_name(self) -> str:
        return self.SPEED_NAMES[self.current_speed_index]

    def local_time_str(self) -> str:
        return self.current_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")

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
        pygame.draw.circle(surface, PANEL_BORDER, (cx, cy), self.radius, 2)

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

        pygame.draw.polygon(surface, ACCENT, [
            (cx, cy - self.radius - 2), (cx - 6, cy - self.radius - 12), (cx + 6, cy - self.radius - 12)])
        heading = math.degrees(yaw) % 360
        text = self.small_font.render(f"{heading:03.0f}°  alt {math.degrees(pitch):+.0f}°", True, LIGHT_GRAY)
        surface.blit(text, (cx - text.get_width() // 2, cy + self.radius + 8))


class StarryNightApp:
    """Main application class for the starry night viewer."""

    MIN_FOV = math.radians(25)
    MAX_FOV = math.radians(110)

    def __init__(self, latitude: float = DEFAULT_LATITUDE, longitude: float = DEFAULT_LONGITUDE):
        pygame.init()
        self.width, self.height = 1200, 800
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Starry Night - Celestial Viewer")

        self.latitude = math.radians(latitude)
        self.longitude = math.radians(longitude)
        self.sin_lat = math.sin(self.latitude)
        self.cos_lat = math.cos(self.latitude)

        self.objects: List[CelestialObject] = []
        self.clock = pygame.time.Clock()
        self.running = True
        self.mouse_pos = None
        self.dragging = False
        self.drag_moved = False
        self.time_manager = TimeManager()
        self.show_controls = True
        self.show_labels = True
        self.show_constellations = True
        self.always_night = False  # ignore daylight: keep the sky dark
        self.selected_object: Optional[CelestialObject] = None
        self.hovered_object: Optional[CelestialObject] = None
        self.compass = Compass(56)

        # Camera: yaw 0 = north; start looking south (where planets appear
        # from the northern hemisphere), slightly upward
        self.yaw = math.pi
        self.pitch = math.radians(25)
        self.fov = math.radians(70)

        self.fonts = {size: pygame.font.SysFont(None, size) for size in (18, 20, 24, 26, 30)}
        self.sky_background = None
        self.sky_background_key = None
        self.sun_alt_deg = -90.0
        self.last_lst = None

        self.create_celestial_objects()
        self.update_sky(force=True)

    # ------------------------------------------------------------------ setup

    def create_celestial_objects(self):
        """Create catalog stars, background stars, galaxies, and solar-system bodies."""
        self.stars_by_name = {}
        for name, ra_h, dec_d, mag, color, dist, constellation in STARS:
            obj = CelestialObject(
                name, math.radians(ra_h * 15), math.radians(dec_d), mag,
                STAR_COLORS[color], "star",
                info=f"Star in {constellation}", distance_ly=dist,
                constellation=constellation, labeled=mag <= 0.5)
            self.stars_by_name[name] = obj
            self.objects.append(obj)

        # Constellation stick figures as star-object pairs
        self.constellation_segments = []
        for constellation, pairs in CONSTELLATION_LINES.items():
            for a, b in pairs:
                self.constellation_segments.append(
                    (self.stars_by_name[a], self.stars_by_name[b]))

        # Faint anonymous background stars, fixed on the celestial sphere
        for i in range(600):
            ra = random.uniform(0, 2 * math.pi)
            dec = math.asin(random.uniform(-1.0, 1.0))
            mag = random.uniform(3.5, 6.5)
            color = random.choice(list(STAR_COLORS.values()))
            self.objects.append(CelestialObject(
                f"Star {i + 1}", ra, dec, round(mag, 1), color, "star",
                info="Background star"))

        for name, ra_h, dec_d, mag, dist, info in GALAXIES:
            self.objects.append(CelestialObject(
                name, math.radians(ra_h * 15), math.radians(dec_d), mag,
                (200, 170, 255), "galaxy", info=info, distance_ly=dist, labeled=True))

        # Solar-system bodies; RA/Dec filled in by update_sky()
        self.sun = CelestialObject("Sun", 0, 0, -26.7, (255, 240, 180), "sun",
                                   info="Our star", labeled=True)
        self.moon = CelestialObject("Moon", 0, 0, -12.7, (225, 225, 210), "moon",
                                    info="Earth's natural satellite", labeled=True)
        self.planets = []
        planet_info = {
            "Mercury": "Closest planet to the Sun", "Venus": "Hottest planet",
            "Mars": "The Red Planet", "Jupiter": "Largest planet",
            "Saturn": "Ringed planet", "Uranus": "Ice giant",
            "Neptune": "Windiest planet",
        }
        for name in PLANET_COLORS:
            planet = CelestialObject(
                name, 0, 0, PLANET_MAGNITUDES[name], PLANET_COLORS[name],
                "planet", info=planet_info[name], labeled=True)
            self.planets.append(planet)
        self.objects.extend([self.sun, self.moon] + self.planets)

        self.moon_illumination = 0.0
        self.moon_waxing = True
        self.moon_phase_name = ""

    # ------------------------------------------------------------ sky updates

    def update_sky(self, force: bool = False):
        """Recompute ephemerides and horizontal coordinates for the current sim time."""
        now = self.time_manager.current_time
        lst = astronomy.local_sidereal_time(now, self.longitude)
        if not force and self.last_lst is not None and abs(lst - self.last_lst) < 1e-7:
            return
        self.last_lst = lst

        ra, dec, dist = astronomy.sun_position(now)
        self.sun.set_equatorial(ra, dec)
        self.sun.distance_au = dist
        ra, dec, dist_km = astronomy.moon_position(now)
        self.moon.set_equatorial(ra, dec)
        self.moon.distance_km = dist_km
        self.moon_illumination, self.moon_waxing, self.moon_phase_name = astronomy.moon_phase(now)
        for planet in self.planets:
            ra, dec, dist = astronomy.planet_position(planet.name, now)
            planet.set_equatorial(ra, dec)
            planet.distance_au = dist

        for obj in self.objects:
            obj.update_horizontal(lst, self.sin_lat, self.cos_lat)
        self.sun_alt_deg = math.degrees(self.sun.altitude)
        self.refresh_sky_background()

    def effective_sun_alt(self) -> float:
        """Sun altitude used for sky color and star visibility."""
        return -90.0 if self.always_night else self.sun_alt_deg

    def refresh_sky_background(self):
        """(Re)render the sky gradient; cached per (size, sun altitude degree)."""
        key = (self.width, self.height, round(self.effective_sun_alt()))
        if key == self.sky_background_key:
            return
        self.sky_background_key = key
        zenith, horizon_col = sky_palette(self.effective_sun_alt())
        self.sky_background = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            t = y / max(1, self.height - 1)
            pygame.draw.line(self.sky_background, lerp_color(zenith, horizon_col, t),
                             (0, y), (self.width, y))

    # ------------------------------------------------------------- projection

    def focal_length(self) -> float:
        return (self.height / 2) / math.tan(self.fov / 2)

    def project(self, direction: Tuple[float, float, float], clip: bool = True):
        """Project a world direction vector to screen coordinates.

        Returns None when the direction is behind the camera, or (with
        clip=True) well outside the screen.
        """
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
        if clip and not (-80 <= sx <= self.width + 80 and -80 <= sy <= self.height + 80):
            return None
        return (sx, sy)

    # ----------------------------------------------------------------- events

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = max(640, event.w), max(480, event.h)
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                self.sky_background_key = None
                self.refresh_sky_background()
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
            self.update_sky(force=True)
        elif key == pygame.K_c:
            self.show_controls = not self.show_controls
        elif key == pygame.K_l:
            self.show_labels = not self.show_labels
        elif key == pygame.K_k:
            self.show_constellations = not self.show_constellations
        elif key == pygame.K_n:
            self.always_night = not self.always_night
            self.refresh_sky_background()
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
        """Select the object closest to the click, if any is near."""
        best, best_dist = None, 18.0
        for obj in self.objects:
            if obj.screen_pos is None or not obj.is_visible:
                continue
            dist = math.hypot(pos[0] - obj.screen_pos[0], pos[1] - obj.screen_pos[1])
            dist -= obj.screen_size
            if dist < best_dist:
                best, best_dist = obj, dist
        self.selected_object = best

    # ----------------------------------------------------------------- update

    def update(self):
        delta_time = self.clock.get_time() / 1000.0
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
        self.update_sky()

    # ------------------------------------------------------------------- draw

    def draw(self):
        self.screen.blit(self.sky_background, (0, 0))
        limit = limiting_magnitude(self.effective_sun_alt())
        if self.show_constellations and limit > 3.0:
            self.draw_constellations()
        self.draw_objects(limit)
        self.draw_horizon()
        self.compass.draw(self.screen, (self.width - 90, 96), self.yaw, self.pitch)
        self.draw_hud()
        if self.show_controls:
            self.draw_controls()
        if self.selected_object:
            self.draw_info_panel(self.selected_object)
        pygame.display.flip()

    def draw_horizon(self):
        """Draw the horizon line with cardinal direction markers."""
        segment = []
        segments = []
        for deg in range(0, 361, 3):
            direction = (math.sin(math.radians(deg)), 0.0, math.cos(math.radians(deg)))
            pos = self.project(direction)
            if pos:
                segment.append(pos)
            else:
                if len(segment) >= 2:
                    segments.append(segment)
                segment = []
        if len(segment) >= 2:
            segments.append(segment)
        for seg in segments:
            pygame.draw.lines(self.screen, HORIZON_COLOR, False, seg, 2)

        font = self.fonts[26]
        for deg, label in ((0, "N"), (90, "E"), (180, "S"), (270, "W")):
            direction = (math.sin(math.radians(deg)), 0.0, math.cos(math.radians(deg)))
            pos = self.project(direction)
            if pos:
                text = font.render(label, True, ACCENT)
                self.screen.blit(text, (pos[0] - text.get_width() // 2, pos[1] + 8))

    def draw_constellations(self):
        """Draw constellation stick figures and names."""
        font = self.fonts[18]
        name_points = {}
        for star_a, star_b in self.constellation_segments:
            if star_a.altitude < -0.02 and star_b.altitude < -0.02:
                continue
            pos_a = self.project(star_a.direction(), clip=False)
            pos_b = self.project(star_b.direction(), clip=False)
            if pos_a and pos_b:
                pygame.draw.line(self.screen, CONSTELLATION_COLOR, pos_a, pos_b, 1)
                name_points.setdefault(star_a.constellation, []).append(pos_a)
        for constellation, points in name_points.items():
            cx = sum(p[0] for p in points) / len(points)
            cy = sum(p[1] for p in points) / len(points)
            if 0 <= cx <= self.width and 0 <= cy <= self.height:
                text = font.render(constellation, True, CONSTELLATION_COLOR)
                self.screen.blit(text, (cx - text.get_width() // 2, cy + 12))

    def object_radius(self, obj: CelestialObject) -> float:
        zoom_scale = math.sqrt(self.focal_length() / ((self.height / 2) / math.tan(math.radians(35))))
        if obj.type in ("sun", "moon"):
            return 15 * zoom_scale
        if obj.type == "planet":
            return max(3.0, (6.5 - min(obj.mag, 5.5)) * 0.8) * zoom_scale
        return max(1.0, (6.5 - obj.mag) * 0.55) * zoom_scale

    def draw_objects(self, limit: float):
        ticks = pygame.time.get_ticks() / 1000.0
        self.hovered_object = None
        label_font = self.fonts[18]

        for obj in self.objects:
            obj.screen_pos = None
            if not obj.is_visible or obj.altitude < -0.01:
                continue
            # Twilight/daylight visibility: fade stars out as the sky brightens
            fade = 1.0
            if obj.type in ("star", "galaxy", "planet"):
                fade_mag = min(obj.mag, 5.5) if obj.type in ("galaxy", "planet") else obj.mag
                fade = max(0.0, min(1.0, (limit - fade_mag) / 1.5))
                if fade <= 0.0:
                    continue
            pos = self.project(obj.direction())
            if pos is None:
                continue
            obj.screen_pos = pos
            obj.screen_size = self.object_radius(obj)

            x, y = int(pos[0]), int(pos[1])
            radius = max(1, int(obj.screen_size))

            if obj.type == "sun":
                self.draw_sun(x, y, radius)
            elif obj.type == "moon":
                self.draw_moon(x, y, radius)
            else:
                color = obj.color
                if obj.type == "star" and obj.mag > 3.5:
                    twinkle = 0.8 + 0.2 * math.sin(ticks * 2.5 + obj.twinkle_phase)
                    fade *= twinkle
                if fade < 1.0:
                    color = tuple(int(c * fade) for c in color)
                if obj.labeled and radius >= 3:
                    glow_radius = radius * 2
                    glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (*obj.color, int(60 * fade)),
                                       (glow_radius, glow_radius), glow_radius)
                    self.screen.blit(glow, (x - glow_radius, y - glow_radius))
                pygame.draw.circle(self.screen, color, (x, y), radius)

            if obj is self.selected_object:
                pygame.draw.circle(self.screen, ACCENT, (x, y), radius + 8, 2)
            if self.show_labels and obj.labeled:
                text = label_font.render(obj.name, True, LIGHT_GRAY)
                self.screen.blit(text, (x - text.get_width() // 2, y + radius + 4))

            if self.hovered_object is None and obj.is_hovered(self.mouse_pos):
                self.hovered_object = obj

        if self.hovered_object and self.hovered_object is not self.selected_object:
            self.draw_tooltip(self.hovered_object)

    def draw_sun(self, x: int, y: int, radius: int):
        glow_radius = radius * 3
        glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        for r, alpha in ((glow_radius, 30), (int(glow_radius * 0.6), 60)):
            pygame.draw.circle(glow, (255, 230, 150, alpha), (glow_radius, glow_radius), r)
        self.screen.blit(glow, (x - glow_radius, y - glow_radius))
        pygame.draw.circle(self.screen, (255, 244, 200), (x, y), radius)

    def draw_moon(self, x: int, y: int, radius: int):
        """Moon with an approximate phase: a shadow disc slides off the lit disc."""
        size = radius * 2 + 6
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        pygame.draw.circle(surf, (228, 228, 214), (center, center), radius)
        # Shadow slides toward the unlit limb; waxing moon is lit on the right
        offset = 2.2 * radius * self.moon_illumination
        direction = -1 if self.moon_waxing else 1
        zenith, _ = sky_palette(self.effective_sun_alt())
        shadow_center = (center + direction * offset, center)
        pygame.draw.circle(surf, (*zenith, 245), shadow_center, radius * 1.02)
        self.screen.blit(surf, (x - center, y - center))
        pygame.draw.circle(self.screen, (160, 160, 150), (x, y), radius, 1)

    def draw_tooltip(self, obj: CelestialObject):
        x, y = obj.screen_pos
        name_text = self.fonts[24].render(obj.name, True, WHITE)
        parts = [obj.constellation if obj.constellation else obj.type.capitalize()]
        if obj.type not in ("sun", "moon"):
            parts.append(f"mag {obj.mag:g}")
        dist = obj.distance_text()
        if dist:
            parts.append(dist.replace("Distance: ", ""))
        info_text = self.fonts[18].render(" | ".join(parts), True, LIGHT_BLUE)
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
        """Top bar with time, speed, play state, and observing conditions."""
        bar = pygame.Surface((self.width, 42), pygame.SRCALPHA)
        bar.fill((10, 12, 28, 200))
        self.screen.blit(bar, (0, 0))

        state = "PLAYING" if self.time_manager.is_playing else "PAUSED"
        state_color = (140, 255, 140) if self.time_manager.is_playing else ACCENT
        self.screen.blit(self.fonts[24].render(
            f"Time: {self.time_manager.local_time_str()}", True, WHITE), (16, 12))
        self.screen.blit(self.fonts[24].render(
            f"Speed: {self.time_manager.get_current_speed_name()}", True, LIGHT_GRAY), (300, 12))
        self.screen.blit(self.fonts[24].render(state, True, state_color), (560, 12))

        lat_deg = math.degrees(self.latitude)
        lon_deg = math.degrees(self.longitude)
        location = (f"{abs(lat_deg):.1f}°{'N' if lat_deg >= 0 else 'S'} "
                    f"{abs(lon_deg):.1f}°{'E' if lon_deg >= 0 else 'W'}")
        loc_text = self.fonts[20].render(
            f"{location} | Sun {self.sun_alt_deg:+.0f}° | Moon {self.moon_illumination:.0%} {self.moon_phase_name}",
            True, GRAY)
        self.screen.blit(loc_text, (self.width - loc_text.get_width() - 190, 14))
        if self.always_night:
            badge = self.fonts[20].render("ALWAYS NIGHT (N to disable)", True, ACCENT)
            self.screen.blit(badge, (self.width - badge.get_width() - 190, 48))

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
            ("K", "constellations"),
            ("N", "always night on/off"),
            ("L", "toggle labels"),
            ("T", "hide/show selection"),
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
        type_names = {"sun": "Star (our own)", "moon": "Moon", "planet": "Planet",
                      "galaxy": "Galaxy", "star": "Star"}
        lines = [(type_names[obj.type], LIGHT_BLUE)]
        if obj.constellation:
            lines.append((f"Constellation: {obj.constellation}", LIGHT_GRAY))
        dist = obj.distance_text()
        if dist:
            lines.append((dist, LIGHT_GRAY))
        if obj.type == "moon":
            lines.append((f"Phase: {self.moon_phase_name} ({self.moon_illumination:.0%} lit)", LIGHT_GRAY))
        elif obj.type not in ("sun",):
            lines.append((f"Magnitude: {obj.mag:g}", LIGHT_GRAY))
        lines.append((f"Azimuth {math.degrees(obj.azimuth):.1f}° | Altitude {math.degrees(obj.altitude):+.1f}°",
                      LIGHT_GRAY))
        if obj.info:
            lines.append((obj.info, WHITE))
        lines.append(("T: hide/show   ESC: deselect", GRAY))

        width, row_h = 360, 22
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
    parser = argparse.ArgumentParser(description="Starry Night - Celestial Viewer")
    parser.add_argument("--lat", type=float, default=DEFAULT_LATITUDE,
                        help="observer latitude in degrees (default: Amsterdam)")
    parser.add_argument("--lon", type=float, default=DEFAULT_LONGITUDE,
                        help="observer longitude in degrees, east positive")
    args = parser.parse_args()
    app = StarryNightApp(latitude=args.lat, longitude=args.lon)
    app.run()


if __name__ == "__main__":
    main()
