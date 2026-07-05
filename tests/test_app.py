"""Headless integration tests for the viewer (SDL dummy video driver)."""
import datetime
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from starry_night.main import StarryNightApp, limiting_magnitude, sky_palette


@pytest.fixture()
def app():
    application = StarryNightApp()
    yield application
    pygame.quit()


def centered_on(app, obj):
    app.yaw = obj.azimuth
    app.pitch = obj.altitude
    return app.project(obj.direction())


def visible_star(app):
    return next(o for o in app.objects
                if o.type == "star" and o.constellation and o.altitude > 0.2)


def test_rotation_moves_objects(app):
    star = visible_star(app)
    pos = centered_on(app, star)
    assert abs(pos[0] - app.width / 2) < 1 and abs(pos[1] - app.height / 2) < 1
    app.yaw -= 0.2
    moved = app.project(star.direction())
    assert moved and abs(moved[0] - pos[0]) > 20


def test_drag_grabs_the_sky(app):
    star = visible_star(app)
    before = centered_on(app, star)
    app.dragging = True
    pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, pos=(600, 400), rel=(50, 0)))
    app.handle_events()
    after = app.project(star.direction())
    assert after[0] > before[0] + 10  # drag right -> sky moves right

    before = centered_on(app, star)
    pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, pos=(600, 400), rel=(0, 50)))
    app.handle_events()
    after = app.project(star.direction())
    assert after[1] > before[1] + 10  # drag down -> sky moves down


def test_scroll_zooms(app):
    fov = app.fov
    pygame.event.post(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=1))
    app.handle_events()
    assert app.fov < fov


def test_sky_rotates_with_time(app):
    # A star near the celestial equator sweeps ~15 deg/hour across the sky;
    # circumpolar stars circle the pole and barely change azimuth.
    star = next(o for o in app.objects
                if o.type == "star" and o.constellation and abs(o.dec) < math.radians(30))
    az_before = star.azimuth
    app.time_manager.current_time += datetime.timedelta(hours=3)
    app.update_sky()
    assert abs(star.azimuth - az_before) > math.radians(10)


def test_reset_restores_sky(app):
    star = visible_star(app)
    az_before = star.azimuth
    app.time_manager.current_time += datetime.timedelta(hours=6)
    app.update_sky()
    app.handle_key(pygame.K_r)
    assert abs(star.azimuth - az_before) < 1e-6


def test_planets_present_and_positioned(app):
    names = {p.name for p in app.planets}
    assert names == {"Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"}
    for planet in app.planets:
        assert planet.distance_au > 0.2


def test_day_night_cycle():
    palette_night = sky_palette(-40)
    palette_day = sky_palette(30)
    assert sum(palette_day[0]) > sum(palette_night[0]) + 200  # day sky is brighter
    assert limiting_magnitude(-40) > 6  # many stars at night
    assert limiting_magnitude(10) < 0   # (almost) none in daylight


def test_frames_render_and_window_resizes(app):
    for _ in range(3):
        app.update()
        app.draw()
        app.clock.tick(60)
    app.selected_object = app.moon
    app.draw()  # info panel incl. moon phase
    pygame.event.post(pygame.event.Event(pygame.VIDEORESIZE, w=900, h=600))
    app.handle_events()
    app.draw()
    assert app.width == 900 and app.height == 600
