"""
Astronomy helpers: sidereal time, coordinate transforms, and low-precision
ephemerides for the Sun, Moon, and planets.

Conventions: angles in radians unless a name says otherwise. Right
ascension/declination are J2000. Azimuth is measured from north, eastward.
Accuracy is on the order of arcminutes for the Sun/planets and ~0.5 degrees
for the Moon — plenty for a visual planetarium.
"""
import datetime
import math

from .catalog import METEOR_SHOWERS

J2000 = datetime.datetime(2000, 1, 1, 12, tzinfo=datetime.timezone.utc)
OBLIQUITY = math.radians(23.4393)
TWO_PI = 2 * math.pi


def days_since_j2000(dt: datetime.datetime) -> float:
    return (dt - J2000).total_seconds() / 86400.0


def greenwich_sidereal_time(dt: datetime.datetime) -> float:
    d = days_since_j2000(dt)
    return math.radians((280.46061837 + 360.98564736629 * d) % 360.0)


def local_sidereal_time(dt: datetime.datetime, longitude: float) -> float:
    return (greenwich_sidereal_time(dt) + longitude) % TWO_PI


def equatorial_to_horizontal(sin_dec: float, cos_dec: float, ra: float,
                             lst: float, sin_lat: float, cos_lat: float):
    """Convert equatorial (RA/Dec) to horizontal (azimuth, altitude).

    Takes precomputed sin/cos of declination and latitude so the per-frame
    cost per star is only the hour-angle trig.
    """
    ha = lst - ra
    cos_ha = math.cos(ha)
    sin_alt = sin_dec * sin_lat + cos_dec * cos_lat * cos_ha
    alt = math.asin(max(-1.0, min(1.0, sin_alt)))
    az = math.atan2(-cos_dec * math.sin(ha),
                    sin_dec * cos_lat - cos_dec * sin_lat * cos_ha)
    return az % TWO_PI, alt


def ecliptic_to_equatorial(lon: float, lat: float):
    """Convert ecliptic longitude/latitude to (RA, Dec)."""
    sin_lon, cos_lon = math.sin(lon), math.cos(lon)
    sin_lat, cos_lat = math.sin(lat), math.cos(lat)
    sin_e, cos_e = math.sin(OBLIQUITY), math.cos(OBLIQUITY)
    ra = math.atan2(sin_lon * cos_e - math.tan(lat) * sin_e, cos_lon) % TWO_PI
    dec = math.asin(max(-1.0, min(1.0, sin_lat * cos_e + cos_lat * sin_e * sin_lon)))
    return ra, dec


# Keplerian elements and rates per Julian century, valid ~1800-2050
# (JPL "Approximate Positions of the Planets"):
# a (AU), e, I (deg), L (deg), longitude of perihelion (deg), longitude of
# ascending node (deg). "Earth" is the Earth-Moon barycenter.
PLANET_ELEMENTS = {
    "Mercury": ((0.38709927, 0.20563593, 7.00497902, 252.25032350, 77.45779628, 48.33076593),
                (0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689, -0.12534081)),
    "Venus": ((0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255),
              (0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418)),
    "Earth": ((1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0),
              (0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0)),
    "Mars": ((1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891),
             (0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343)),
    "Jupiter": ((5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909),
                (-0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106)),
    "Saturn": ((9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448),
               (-0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794)),
    "Uranus": ((19.18916464, 0.04725744, 0.77263783, 313.23810451, 170.95427630, 74.01692503),
               (-0.00196176, -0.00004397, -0.00242939, 428.48202785, 0.40805281, 0.04240589)),
    "Neptune": ((30.06992276, 0.00859048, 1.77004347, -55.12002969, 44.96476227, 131.78422574),
                (0.00026291, 0.00005105, 0.00035372, 218.45945325, -0.32241464, -0.00508664)),
}


def _solve_kepler(mean_anomaly: float, eccentricity: float) -> float:
    e_anom = mean_anomaly + eccentricity * math.sin(mean_anomaly)
    for _ in range(6):
        e_anom -= ((e_anom - eccentricity * math.sin(e_anom) - mean_anomaly)
                   / (1 - eccentricity * math.cos(e_anom)))
    return e_anom


def heliocentric_position(name: str, dt: datetime.datetime):
    """Heliocentric ecliptic rectangular coordinates (AU)."""
    t_centuries = days_since_j2000(dt) / 36525.0
    elements, rates = PLANET_ELEMENTS[name]
    a, e, incl, mean_lon, peri_lon, node_lon = (
        elements[i] + rates[i] * t_centuries for i in range(6))
    incl, mean_lon, peri_lon, node_lon = map(math.radians, (incl, mean_lon, peri_lon, node_lon))

    mean_anom = (mean_lon - peri_lon) % TWO_PI
    arg_peri = peri_lon - node_lon
    e_anom = _solve_kepler(mean_anom, e)

    # Position in the orbital plane
    xp = a * (math.cos(e_anom) - e)
    yp = a * math.sqrt(1 - e * e) * math.sin(e_anom)

    cw, sw = math.cos(arg_peri), math.sin(arg_peri)
    co, so = math.cos(node_lon), math.sin(node_lon)
    ci, si = math.cos(incl), math.sin(incl)
    x = (cw * co - sw * so * ci) * xp + (-sw * co - cw * so * ci) * yp
    y = (cw * so + sw * co * ci) * xp + (-sw * so + cw * co * ci) * yp
    z = (sw * si) * xp + (cw * si) * yp
    return x, y, z


def _geocentric_radec(gx: float, gy: float, gz: float):
    dist = math.sqrt(gx * gx + gy * gy + gz * gz)
    lon = math.atan2(gy, gx)
    lat = math.asin(gz / dist)
    ra, dec = ecliptic_to_equatorial(lon, lat)
    return ra, dec, dist


def planet_position(name: str, dt: datetime.datetime):
    """Geocentric (RA, Dec, distance in AU) of a planet."""
    px, py, pz = heliocentric_position(name, dt)
    ex, ey, ez = heliocentric_position("Earth", dt)
    return _geocentric_radec(px - ex, py - ey, pz - ez)


def sun_position(dt: datetime.datetime):
    """Geocentric (RA, Dec, distance in AU) of the Sun."""
    ex, ey, ez = heliocentric_position("Earth", dt)
    return _geocentric_radec(-ex, -ey, -ez)


def sun_ecliptic_longitude(dt: datetime.datetime) -> float:
    ex, ey, _ = heliocentric_position("Earth", dt)
    return math.atan2(-ey, -ex) % TWO_PI


def moon_position(dt: datetime.datetime):
    """Geocentric (RA, Dec, distance in km) of the Moon (low precision)."""
    n = days_since_j2000(dt)
    mean_lon = math.radians((218.316 + 13.176396 * n) % 360.0)
    mean_anom = math.radians((134.963 + 13.064993 * n) % 360.0)
    arg_lat = math.radians((93.272 + 13.229350 * n) % 360.0)
    lon = mean_lon + math.radians(6.289) * math.sin(mean_anom)
    lat = math.radians(5.128) * math.sin(arg_lat)
    dist_km = 385001.0 - 20905.0 * math.cos(mean_anom)
    ra, dec = ecliptic_to_equatorial(lon, lat)
    return ra, dec, dist_km


def rise_set_times(radec_at, day_start: datetime.datetime, latitude: float, longitude: float):
    """Find rise and set times in the 24 hours after day_start.

    radec_at is a callable dt -> (ra, dec), so this works for fixed stars
    and moving bodies alike. Scans in 20-minute steps and refines each
    horizon crossing by bisection. Returns (rise, set) datetimes; either
    is None when no crossing occurs (circumpolar or never up).
    """
    sin_lat, cos_lat = math.sin(latitude), math.cos(latitude)

    def altitude(dt):
        ra, dec = radec_at(dt)
        lst = local_sidereal_time(dt, longitude)
        _, alt = equatorial_to_horizontal(
            math.sin(dec), math.cos(dec), ra, lst, sin_lat, cos_lat)
        return alt

    def refine(lo, hi, rising):
        for _ in range(8):
            mid = lo + (hi - lo) / 2
            if (altitude(mid) > 0) == rising:
                hi = mid
            else:
                lo = mid
        return lo + (hi - lo) / 2

    rise = set_ = None
    step = datetime.timedelta(minutes=20)
    prev_time, prev_up = day_start, altitude(day_start) > 0
    for i in range(1, 73):
        t = day_start + step * i
        up = altitude(t) > 0
        if up != prev_up:
            if up and rise is None:
                rise = refine(prev_time, t, rising=True)
            elif not up and set_ is None:
                set_ = refine(prev_time, t, rising=False)
        prev_time, prev_up = t, up
    return rise, set_


def shower_activity(dt: datetime.datetime):
    """Active meteor showers at dt: list of (name, radiant_ra, radiant_dec, rate).

    Rate is the zenithal hourly rate scaled down away from the peak date.
    """
    active = []
    for name, ra_h, dec_d, (month, day), window, zhr in METEOR_SHOWERS:
        delta = None
        for year in (dt.year - 1, dt.year, dt.year + 1):
            peak = datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc)
            days = (dt - peak).total_seconds() / 86400.0
            if delta is None or abs(days) < abs(delta):
                delta = days
        if abs(delta) <= window:
            rate = zhr * math.exp(-abs(delta) / 3.0)
            active.append((name, math.radians(ra_h * 15), math.radians(dec_d), rate))
    return active


def moon_phase(dt: datetime.datetime):
    """Return (illuminated fraction 0..1, waxing flag, phase name)."""
    n = days_since_j2000(dt)
    moon_lon = (math.radians((218.316 + 13.176396 * n) % 360.0)
                + math.radians(6.289) * math.sin(math.radians((134.963 + 13.064993 * n) % 360.0)))
    elongation = (moon_lon - sun_ecliptic_longitude(dt)) % TWO_PI
    illuminated = (1 - math.cos(elongation)) / 2
    waxing = elongation < math.pi
    if illuminated < 0.02:
        name = "New moon"
    elif illuminated > 0.98:
        name = "Full moon"
    elif abs(illuminated - 0.5) < 0.04:
        name = "First quarter" if waxing else "Last quarter"
    elif illuminated < 0.5:
        name = "Waxing crescent" if waxing else "Waning crescent"
    else:
        name = "Waxing gibbous" if waxing else "Waning gibbous"
    return illuminated, waxing, name
