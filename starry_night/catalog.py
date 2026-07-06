"""
Star catalog: the brightest stars of well-known constellations, with J2000
coordinates (RA in decimal hours, Dec in degrees), visual magnitude, an
approximate color class, and distance in light-years where well known (0 =
not listed). Positions are rounded to ~arcminute precision, which is far
below one on-screen pixel for this viewer.
"""

# name, ra_hours, dec_deg, mag, color, dist_ly, constellation
STARS = [
    # Ursa Major (the Big Dipper)
    ("Dubhe", 11.062, 61.75, 1.79, "orange", 123, "Ursa Major"),
    ("Merak", 11.031, 56.38, 2.37, "white", 80, "Ursa Major"),
    ("Phecda", 11.897, 53.69, 2.44, "white", 83, "Ursa Major"),
    ("Megrez", 12.257, 57.03, 3.31, "white", 81, "Ursa Major"),
    ("Alioth", 12.900, 55.96, 1.77, "white", 83, "Ursa Major"),
    ("Mizar", 13.399, 54.93, 2.27, "white", 86, "Ursa Major"),
    ("Alkaid", 13.792, 49.31, 1.86, "blue", 104, "Ursa Major"),
    # Ursa Minor
    ("Polaris", 2.530, 89.26, 1.98, "yellow", 433, "Ursa Minor"),
    ("Kochab", 14.845, 74.16, 2.08, "orange", 131, "Ursa Minor"),
    ("Pherkad", 15.345, 71.83, 3.05, "white", 487, "Ursa Minor"),
    # Cassiopeia
    ("Caph", 0.153, 59.15, 2.27, "yellow", 54, "Cassiopeia"),
    ("Schedar", 0.675, 56.54, 2.24, "orange", 228, "Cassiopeia"),
    ("Navi", 0.945, 60.72, 2.47, "blue", 550, "Cassiopeia"),
    ("Ruchbah", 1.430, 60.24, 2.68, "white", 99, "Cassiopeia"),
    ("Segin", 1.907, 63.67, 3.38, "blue", 410, "Cassiopeia"),
    # Orion
    ("Betelgeuse", 5.919, 7.41, 0.42, "red", 640, "Orion"),
    ("Bellatrix", 5.418, 6.35, 1.64, "blue", 250, "Orion"),
    ("Alnitak", 5.679, -1.94, 1.79, "blue", 740, "Orion"),
    ("Alnilam", 5.604, -1.20, 1.69, "blue", 1340, "Orion"),
    ("Mintaka", 5.533, -0.30, 2.23, "blue", 690, "Orion"),
    ("Saiph", 5.796, -9.67, 2.09, "blue", 650, "Orion"),
    ("Rigel", 5.242, -8.20, 0.13, "blue", 860, "Orion"),
    # Canis Major
    ("Sirius", 6.752, -16.72, -1.46, "white", 8.6, "Canis Major"),
    ("Mirzam", 6.378, -17.96, 1.98, "blue", 500, "Canis Major"),
    ("Adhara", 6.977, -28.97, 1.50, "blue", 430, "Canis Major"),
    ("Wezen", 7.140, -26.39, 1.83, "yellow", 1600, "Canis Major"),
    ("Aludra", 7.401, -29.30, 2.45, "blue", 2000, "Canis Major"),
    # Canis Minor
    ("Procyon", 7.655, 5.22, 0.34, "white", 11.5, "Canis Minor"),
    ("Gomeisa", 7.453, 8.29, 2.89, "blue", 160, "Canis Minor"),
    # Gemini
    ("Castor", 7.577, 31.89, 1.58, "white", 51, "Gemini"),
    ("Pollux", 7.755, 28.03, 1.14, "orange", 34, "Gemini"),
    ("Alhena", 6.629, 16.40, 1.93, "white", 109, "Gemini"),
    # Taurus
    ("Aldebaran", 4.599, 16.51, 0.86, "orange", 65, "Taurus"),
    ("Elnath", 5.438, 28.61, 1.65, "blue", 134, "Taurus"),
    # Auriga
    ("Capella", 5.278, 46.00, 0.08, "yellow", 42.9, "Auriga"),
    ("Menkalinan", 5.992, 44.95, 1.90, "white", 81, "Auriga"),
    # Leo
    ("Regulus", 10.139, 11.97, 1.35, "blue", 79, "Leo"),
    ("Denebola", 11.818, 14.57, 2.14, "white", 36, "Leo"),
    ("Algieba", 10.333, 19.84, 2.08, "orange", 130, "Leo"),
    ("Zosma", 11.235, 20.52, 2.56, "white", 58, "Leo"),
    # Virgo
    ("Spica", 13.420, -11.16, 0.97, "blue", 250, "Virgo"),
    # Bootes
    ("Arcturus", 14.261, 19.18, -0.05, "orange", 36.7, "Bootes"),
    ("Izar", 14.749, 27.07, 2.37, "orange", 202, "Bootes"),
    ("Muphrid", 13.911, 18.40, 2.68, "yellow", 37, "Bootes"),
    # Scorpius
    ("Antares", 16.490, -26.43, 0.96, "red", 550, "Scorpius"),
    ("Shaula", 17.560, -37.10, 1.63, "blue", 570, "Scorpius"),
    ("Dschubba", 16.006, -22.62, 2.32, "blue", 400, "Scorpius"),
    ("Sargas", 17.622, -43.00, 1.87, "yellow", 270, "Scorpius"),
    # Sagittarius
    ("Kaus Australis", 18.403, -34.38, 1.85, "blue", 143, "Sagittarius"),
    ("Nunki", 18.921, -26.30, 2.05, "blue", 228, "Sagittarius"),
    # Lyra
    ("Vega", 18.616, 38.78, 0.03, "blue", 25, "Lyra"),
    ("Sheliak", 18.834, 33.36, 3.52, "white", 960, "Lyra"),
    ("Sulafat", 18.983, 32.69, 3.24, "blue", 620, "Lyra"),
    # Cygnus
    ("Deneb", 20.690, 45.28, 1.25, "white", 2600, "Cygnus"),
    ("Sadr", 20.371, 40.26, 2.23, "yellow", 1800, "Cygnus"),
    ("Albireo", 19.512, 27.96, 3.18, "orange", 430, "Cygnus"),
    ("Fawaris", 19.750, 45.13, 2.87, "blue", 165, "Cygnus"),
    ("Aljanah", 20.770, 33.97, 2.46, "orange", 72, "Cygnus"),
    # Aquila
    ("Altair", 19.846, 8.87, 0.77, "white", 16.7, "Aquila"),
    ("Tarazed", 19.771, 10.61, 2.72, "orange", 395, "Aquila"),
    # Pegasus (the Great Square shares Alpheratz with Andromeda)
    ("Markab", 23.079, 15.21, 2.49, "blue", 133, "Pegasus"),
    ("Scheat", 23.063, 28.08, 2.42, "red", 196, "Pegasus"),
    ("Algenib", 0.220, 15.18, 2.84, "blue", 390, "Pegasus"),
    # Andromeda
    ("Alpheratz", 0.140, 29.09, 2.06, "blue", 97, "Andromeda"),
    ("Mirach", 1.162, 35.62, 2.05, "red", 197, "Andromeda"),
    ("Almach", 2.065, 42.33, 2.26, "orange", 350, "Andromeda"),
    # Perseus
    ("Mirfak", 3.405, 49.86, 1.80, "yellow", 510, "Perseus"),
    ("Algol", 3.136, 40.96, 2.12, "blue", 90, "Perseus"),
    # Crux (Southern Cross)
    ("Acrux", 12.443, -63.10, 0.76, "blue", 320, "Crux"),
    ("Mimosa", 12.795, -59.69, 1.25, "blue", 280, "Crux"),
    ("Gacrux", 12.519, -57.11, 1.64, "red", 89, "Crux"),
    ("Imai", 12.252, -58.75, 2.79, "blue", 345, "Crux"),
    # Centaurus
    ("Rigil Kentaurus", 14.660, -60.83, -0.27, "yellow", 4.4, "Centaurus"),
    ("Hadar", 14.064, -60.37, 0.61, "blue", 390, "Centaurus"),
    # Bright single stars
    ("Canopus", 6.399, -52.70, -0.74, "white", 310, "Carina"),
    ("Fomalhaut", 22.961, -29.62, 1.16, "white", 25, "Piscis Austrinus"),
    ("Achernar", 1.629, -57.24, 0.46, "blue", 139, "Eridanus"),
]

# Constellation stick figures: lines between star names (may cross
# constellation boundaries, e.g. the Great Square of Pegasus).
CONSTELLATION_LINES = {
    "Ursa Major": [("Dubhe", "Merak"), ("Merak", "Phecda"), ("Phecda", "Megrez"),
                   ("Megrez", "Dubhe"), ("Megrez", "Alioth"), ("Alioth", "Mizar"),
                   ("Mizar", "Alkaid")],
    "Ursa Minor": [("Polaris", "Kochab"), ("Kochab", "Pherkad")],
    "Cassiopeia": [("Caph", "Schedar"), ("Schedar", "Navi"), ("Navi", "Ruchbah"),
                   ("Ruchbah", "Segin")],
    "Orion": [("Betelgeuse", "Bellatrix"), ("Betelgeuse", "Alnitak"),
              ("Bellatrix", "Mintaka"), ("Alnitak", "Alnilam"),
              ("Alnilam", "Mintaka"), ("Alnitak", "Saiph"),
              ("Mintaka", "Rigel"), ("Rigel", "Saiph")],
    "Canis Major": [("Sirius", "Mirzam"), ("Sirius", "Wezen"),
                    ("Wezen", "Adhara"), ("Wezen", "Aludra")],
    "Canis Minor": [("Procyon", "Gomeisa")],
    "Gemini": [("Castor", "Pollux"), ("Pollux", "Alhena")],
    "Taurus": [("Aldebaran", "Elnath")],
    "Auriga": [("Capella", "Menkalinan"), ("Menkalinan", "Elnath"),
               ("Elnath", "Capella")],
    "Leo": [("Regulus", "Algieba"), ("Algieba", "Zosma"),
            ("Zosma", "Denebola"), ("Denebola", "Regulus")],
    "Bootes": [("Arcturus", "Izar"), ("Arcturus", "Muphrid")],
    "Scorpius": [("Dschubba", "Antares"), ("Antares", "Shaula"),
                 ("Shaula", "Sargas")],
    "Sagittarius": [("Kaus Australis", "Nunki")],
    "Lyra": [("Vega", "Sheliak"), ("Sheliak", "Sulafat"), ("Sulafat", "Vega")],
    "Cygnus": [("Deneb", "Sadr"), ("Sadr", "Albireo"), ("Sadr", "Fawaris"),
               ("Sadr", "Aljanah")],
    "Aquila": [("Altair", "Tarazed")],
    "Pegasus": [("Markab", "Scheat"), ("Scheat", "Alpheratz"),
                ("Alpheratz", "Algenib"), ("Algenib", "Markab")],
    "Andromeda": [("Alpheratz", "Mirach"), ("Mirach", "Almach")],
    "Perseus": [("Mirfak", "Algol")],
    "Crux": [("Acrux", "Gacrux"), ("Mimosa", "Imai")],
    "Centaurus": [("Rigil Kentaurus", "Hadar")],
}

# name, ra_hours, dec_deg, mag, dist_ly, description
GALAXIES = [
    ("Andromeda Galaxy", 0.712, 41.27, 3.4, 2.5e6, "Closest large galaxy to the Milky Way"),
    ("Whirlpool Galaxy", 13.498, 47.20, 8.4, 23e6, "Grand-design spiral galaxy"),
    ("Sombrero Galaxy", 12.666, -11.62, 8.0, 29e6, "Galaxy with a prominent dust lane"),
]

# Deep-sky showpieces (mostly Messier objects).
# name, alias, ra_hours, dec_deg, mag, type, dist_ly, description
# type: "nebula", "planetary", "open_cluster", "globular", "galaxy"
DEEP_SKY = [
    ("Orion Nebula", "M42", 5.588, -5.39, 4.0, "nebula", 1344, "Bright stellar nursery in Orion's sword"),
    ("Pleiades", "M45", 3.790, 24.12, 1.6, "open_cluster", 444, "The Seven Sisters open cluster"),
    ("Hercules Cluster", "M13", 16.695, 36.46, 5.8, "globular", 22200, "Great globular cluster in Hercules"),
    ("Ring Nebula", "M57", 18.893, 33.03, 8.8, "planetary", 2300, "Famous planetary nebula in Lyra"),
    ("Dumbbell Nebula", "M27", 19.994, 22.72, 7.4, "planetary", 1360, "Bright planetary nebula in Vulpecula"),
    ("Crab Nebula", "M1", 5.575, 22.01, 8.4, "nebula", 6500, "Supernova remnant from the year 1054"),
    ("Lagoon Nebula", "M8", 18.060, -24.38, 6.0, "nebula", 4100, "Emission nebula in Sagittarius"),
    ("Omega Nebula", "M17", 18.340, -16.18, 6.0, "nebula", 5000, "Also known as the Swan Nebula"),
    ("Trifid Nebula", "M20", 18.030, -23.03, 6.3, "nebula", 5200, "Three-lobed emission nebula"),
    ("Eagle Nebula", "M16", 18.313, -13.78, 6.4, "nebula", 5700, "Home of the Pillars of Creation"),
    ("Beehive Cluster", "M44", 8.670, 19.98, 3.7, "open_cluster", 577, "Naked-eye open cluster in Cancer"),
    ("Wild Duck Cluster", "M11", 18.851, -6.27, 6.3, "open_cluster", 6200, "Compact open cluster in Scutum"),
    ("Gemini Cluster", "M35", 6.148, 24.34, 5.3, "open_cluster", 2800, "Rich open cluster at Gemini's foot"),
    ("Little Beehive", "M41", 6.767, -20.73, 4.5, "open_cluster", 2300, "Open cluster south of Sirius"),
    ("Ptolemy Cluster", "M7", 17.897, -34.79, 3.3, "open_cluster", 980, "Naked-eye cluster in Scorpius"),
    ("Butterfly Cluster", "M6", 17.668, -32.25, 4.2, "open_cluster", 1600, "Open cluster shaped like a butterfly"),
    ("Double Cluster", "NGC 869/884", 2.320, 57.13, 3.7, "open_cluster", 7500, "Twin open clusters in Perseus"),
    ("Sagittarius Cluster", "M22", 18.607, -23.90, 5.1, "globular", 10600, "One of the brightest globulars"),
    ("M3", "M3", 13.703, 28.38, 6.2, "globular", 33900, "Globular with ~500,000 stars"),
    ("M5", "M5", 15.310, 2.08, 5.6, "globular", 24500, "One of the oldest known globulars"),
    ("M92", "M92", 17.285, 43.13, 6.4, "globular", 26700, "Second globular in Hercules"),
    ("Omega Centauri", "NGC 5139", 13.446, -47.48, 3.9, "globular", 15800, "Largest globular of the Milky Way"),
    ("47 Tucanae", "NGC 104", 0.401, -72.08, 4.1, "globular", 13000, "Southern showpiece globular"),
    ("Carina Nebula", "NGC 3372", 10.750, -59.87, 3.0, "nebula", 8500, "Giant southern nebula around Eta Carinae"),
    ("Triangulum Galaxy", "M33", 1.564, 30.66, 5.7, "galaxy", 2.7e6, "Third-largest galaxy of the Local Group"),
    ("Bode's Galaxy", "M81", 9.926, 69.07, 6.9, "galaxy", 12e6, "Bright spiral near the Big Dipper"),
]

# Galactic north pole (J2000), used to paint the Milky Way band
GALACTIC_POLE_RA_HOURS = 12.857
GALACTIC_POLE_DEC_DEG = 27.13

# Major meteor showers.
# name, radiant ra_hours, radiant dec_deg, peak (month, day), active window
# in days around the peak, zenithal hourly rate at peak
METEOR_SHOWERS = [
    ("Quadrantids", 15.30, 49.5, (1, 3), 4, 110),
    ("Lyrids", 18.07, 34.0, (4, 22), 5, 18),
    ("Eta Aquariids", 22.47, -1.0, (5, 6), 12, 50),
    ("Perseids", 3.07, 58.0, (8, 12), 16, 100),
    ("Orionids", 6.35, 15.6, (10, 21), 14, 20),
    ("Leonids", 10.27, 21.8, (11, 17), 6, 15),
    ("Geminids", 7.55, 32.4, (12, 14), 7, 150),
]
