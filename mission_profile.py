"""
Mission definition for OpenConcept-based battery sizing.
Current values include propulsion + avionics loads.
"""

MISSION_SEGMENTS = [
    {"name": "takeoff",      "duration_s": 5, "current_A": 10},
    {"name": "cruise",       "duration_s": 57.0,  "current_A": 9.21},
    {"name": "climb",        "duration_s": 11.0,  "current_A": 9},
    {"name": "hover_ascent", "duration_s": 29.0,  "current_A": 24.3},
    {"name": "hover_descent","duration_s": 25.0,  "current_A": 14.23},
    {"name": "hover_hold",   "duration_s": 32.0,  "current_A": 16.86},
    {"name": "landing",      "duration_s": 40.0,  "current_A": 8},
    {"name": "transition",   "duration_s": 20.0,  "current_A": 18.9},
]
