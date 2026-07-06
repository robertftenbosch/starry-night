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


def test_always_night_keeps_the_sky_dark(app):
    # Force midday, then toggle always-night: the sky must go dark and
    # stars must become visible again
    app.time_manager.current_time = datetime.datetime(2026, 7, 5, 11, 0,
                                                      tzinfo=datetime.timezone.utc)
    app.update_sky(force=True)
    assert app.sun_alt_deg > 30
    day_background = app.sky_background.get_at((10, app.height // 2))
    assert limiting_magnitude(app.effective_sun_alt()) < 0

    app.handle_key(pygame.K_n)
    night_background = app.sky_background.get_at((10, app.height // 2))
    assert sum(night_background[:3]) < sum(day_background[:3]) - 200
    assert limiting_magnitude(app.effective_sun_alt()) > 6
    app.draw()

    app.handle_key(pygame.K_n)  # toggles back
    assert app.effective_sun_alt() == app.sun_alt_deg


def test_deep_sky_objects_present(app):
    by_alias = {o.alias: o for o in app.objects if o.alias}
    assert by_alias["M42"].name == "Orion Nebula"
    assert by_alias["M45"].type == "open_cluster"
    assert by_alias["M13"].type == "globular"
    assert by_alias["M57"].type == "planetary"
    assert len(by_alias) >= 25


def test_search_matches_names_aliases_and_constellations(app):
    labels = [label for label, _ in app.find_matches("orio")]
    assert any("Orion Nebula" in label for label in labels)
    assert any("constellation" in label for label in labels)
    label, target = app.find_matches("m42")[0]
    assert target.name == "Orion Nebula"
    assert app.find_matches("jupit")[0][1].name == "Jupiter"
    assert app.find_matches("xyzzy") == []


def test_search_go_to_eases_camera_toward_target(app):
    jupiter = next(p for p in app.planets if p.name == "Jupiter")
    app.open_input("search")
    app.input_text = "jupiter"
    app.search_matches = app.find_matches(app.input_text)
    app.commit_search()
    assert app.selected_object is jupiter and app.follow_target is jupiter
    before = abs(app.wrap_angle(jupiter.azimuth - app.yaw))
    for _ in range(60):
        app.follow_camera(1 / 30)
    after = abs(app.wrap_angle(jupiter.azimuth - app.yaw))
    assert after < before / 10 and after < math.radians(1)
    assert app.follow_target is None  # transient go-to stops on arrival


def test_follow_tracks_moving_object_through_time(app):
    app.selected_object = app.moon
    app.handle_key(pygame.K_f)
    for _ in range(30):
        app.follow_camera(1 / 30)
    app.time_manager.current_time += datetime.timedelta(hours=2)
    app.update_sky()
    app.follow_camera(1 / 30)
    assert abs(app.wrap_angle(app.moon.azimuth - app.yaw)) < math.radians(1.5)
    assert app.follow_target is app.moon  # persistent follow keeps tracking


def test_date_jump_sets_simulation_time(app):
    app.open_input("date")
    app.input_text = "1990-05-17 22:30"
    app.commit_date()
    assert app.input_mode is None
    local = app.time_manager.current_time.astimezone()
    assert (local.year, local.month, local.day, local.hour, local.minute) == (1990, 5, 17, 22, 30)

    app.open_input("date")
    app.input_text = "not a date"
    app.commit_date()
    assert app.input_mode == "date" and app.input_error


def test_rise_set_times_for_sun_and_stars(app):
    app.open_input("date")
    app.input_text = "2026-07-05 12:00"
    app.commit_date()
    # Amsterdam summer: sunrise ~05:30, sunset ~22:00 (geometric, no refraction)
    sun_text = app.rise_set_text(app.sun)
    assert "Rises 05:" in sun_text and ("Sets 21:" in sun_text or "Sets 22:" in sun_text)
    polaris = app.stars_by_name["Polaris"]
    assert "Circumpolar" in app.rise_set_text(polaris)
    acrux = app.stars_by_name["Acrux"]  # dec -63: never up from Amsterdam
    assert "Below the horizon" in app.rise_set_text(acrux)


def test_meteor_shower_activity():
    from starry_night import astronomy
    peak = datetime.datetime(2026, 8, 12, tzinfo=datetime.timezone.utc)
    active = astronomy.shower_activity(peak)
    assert any(name == "Perseids" and rate > 80 for name, _, _, rate in active)
    quiet = astronomy.shower_activity(datetime.datetime(2026, 3, 10, tzinfo=datetime.timezone.utc))
    assert quiet == []


def test_visual_modes_render(app):
    # Grids, night vision, milky way, meteors, and the input panel all draw
    app.grid_mode = 1
    app.draw()
    app.grid_mode = 2
    app.night_vision = True
    app.meteors.append(app.make_meteor(math.radians(180), math.radians(45),
                                       pygame.time.get_ticks() / 1000.0))
    app.draw()
    app.open_input("search")
    app.input_text = "m4"
    app.search_matches = app.find_matches(app.input_text)
    app.draw()
    assert len(app.milky_way) > 300


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
