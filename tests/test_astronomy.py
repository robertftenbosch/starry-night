"""Sanity checks for the astronomy module against well-known facts."""
import datetime
import math

from starry_night import astronomy

UTC = datetime.timezone.utc
AMSTERDAM_LAT = math.radians(52.37)
AMSTERDAM_LON = math.radians(4.90)


def horizontal(ra, dec, dt, lat=AMSTERDAM_LAT, lon=AMSTERDAM_LON):
    lst = astronomy.local_sidereal_time(dt, lon)
    return astronomy.equatorial_to_horizontal(
        math.sin(dec), math.cos(dec), ra, lst, math.sin(lat), math.cos(lat))


def test_polaris_altitude_equals_latitude():
    """Polaris sits within ~1 degree of the observer's latitude, always."""
    polaris_ra = math.radians(2.530 * 15)
    polaris_dec = math.radians(89.26)
    for month in (1, 4, 7, 10):
        dt = datetime.datetime(2026, month, 15, 22, tzinfo=UTC)
        az, alt = horizontal(polaris_ra, polaris_dec, dt)
        assert abs(math.degrees(alt) - 52.37) < 1.0
        assert math.degrees(az) < 2 or math.degrees(az) > 358  # due north


def test_sun_declination_at_equinox_and_solstice():
    _, dec, _ = astronomy.sun_position(datetime.datetime(2026, 3, 20, 12, tzinfo=UTC))
    assert abs(math.degrees(dec)) < 1.0
    _, dec, _ = astronomy.sun_position(datetime.datetime(2026, 6, 21, 12, tzinfo=UTC))
    assert abs(math.degrees(dec) - 23.4) < 0.5


def test_sun_altitude_at_amsterdam_summer_noon():
    """Max sun altitude = 90 - latitude + declination (~61 deg in June)."""
    best = max(
        math.degrees(horizontal(*astronomy.sun_position(
            datetime.datetime(2026, 6, 21, 8, tzinfo=UTC)
            + datetime.timedelta(minutes=10 * i))[:2],
            datetime.datetime(2026, 6, 21, 8, tzinfo=UTC) + datetime.timedelta(minutes=10 * i))[1])
        for i in range(48))
    assert abs(best - 61.0) < 1.5


def test_sun_is_down_at_amsterdam_midnight():
    dt = datetime.datetime(2026, 7, 5, 0, 30, tzinfo=UTC)
    _, alt = horizontal(*astronomy.sun_position(dt)[:2], dt)
    assert math.degrees(alt) < -5


def test_sidereal_rotation_rate():
    """The sky advances ~15 degrees per hour (one rotation per sidereal day)."""
    dt1 = datetime.datetime(2026, 7, 5, 22, tzinfo=UTC)
    dt2 = dt1 + datetime.timedelta(hours=1)
    lst1 = astronomy.local_sidereal_time(dt1, 0)
    lst2 = astronomy.local_sidereal_time(dt2, 0)
    delta = math.degrees((lst2 - lst1) % (2 * math.pi))
    assert abs(delta - 15.04) < 0.05


def test_earth_sun_distance_is_one_au():
    for month in (1, 4, 7, 10):
        _, _, dist = astronomy.sun_position(datetime.datetime(2026, month, 1, tzinfo=UTC))
        assert 0.97 < dist < 1.03


def test_planet_distances_within_physical_bounds():
    bounds = {"Mercury": (0.5, 1.5), "Venus": (0.25, 1.75), "Mars": (0.37, 2.7),
              "Jupiter": (3.9, 6.5), "Saturn": (8.0, 11.1),
              "Uranus": (17.3, 21.1), "Neptune": (28.9, 31.3)}
    for month in (1, 7):
        dt = datetime.datetime(2026, month, 1, tzinfo=UTC)
        for name, (lo, hi) in bounds.items():
            _, _, dist = astronomy.planet_position(name, dt)
            assert lo < dist < hi, f"{name}: {dist} AU outside [{lo}, {hi}]"


def test_planets_stay_near_the_ecliptic():
    """Geocentric ecliptic latitude of any planet is at most ~9 degrees."""
    for month in (2, 8):
        dt = datetime.datetime(2026, month, 1, tzinfo=UTC)
        sun_ra, sun_dec, _ = astronomy.sun_position(dt)
        for name in astronomy.PLANET_ELEMENTS:
            if name == "Earth":
                continue
            _, dec, _ = astronomy.planet_position(name, dt)
            assert abs(math.degrees(dec)) < 23.44 + 9.5


def test_moon_moves_thirteen_degrees_per_day():
    dt = datetime.datetime(2026, 7, 5, tzinfo=UTC)
    ra1, dec1, _ = astronomy.moon_position(dt)
    ra2, dec2, _ = astronomy.moon_position(dt + datetime.timedelta(days=1))
    separation = math.degrees(math.acos(max(-1, min(1,
        math.sin(dec1) * math.sin(dec2)
        + math.cos(dec1) * math.cos(dec2) * math.cos(ra1 - ra2)))))
    assert 10 < separation < 16


def test_moon_phase_cycles_in_a_synodic_month():
    dt = datetime.datetime(2026, 7, 5, tzinfo=UTC)
    k1, _, _ = astronomy.moon_phase(dt)
    k2, _, _ = astronomy.moon_phase(dt + datetime.timedelta(days=29.53 / 2))
    k3, _, _ = astronomy.moon_phase(dt + datetime.timedelta(days=29.53))
    assert abs((k1 + k2) - 1.0) < 0.25  # half a cycle later: opposite phase
    assert abs(k3 - k1) < 0.15          # full cycle later: same phase
    for days in range(0, 30, 3):
        k, _, name = astronomy.moon_phase(dt + datetime.timedelta(days=days))
        assert 0.0 <= k <= 1.0 and name


def test_moon_distance_in_physical_range():
    for days in range(0, 28, 4):
        dt = datetime.datetime(2026, 7, 1, tzinfo=UTC) + datetime.timedelta(days=days)
        _, _, dist_km = astronomy.moon_position(dt)
        assert 356000 < dist_km < 407000
