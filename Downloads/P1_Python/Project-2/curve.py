"""
curve.py
Author: AI assistant
Purpose: Spline curve utilities for roller coaster track using Catmull-Rom interpolation
"""

import numpy as np

# Extended control points for a lengthy roller coaster track
# This creates a long, extensive travel path instead of a short loop
control_points = [
    # Starting section - gentle beginning
    (0.0, 0.0, 0.0),      # Start point
    (10.0, 0.0, 5.0),     # Gentle curve
    (25.0, 2.0, 15.0),    # First hill
    (45.0, 0.0, 25.0),    # Downhill
    
    # First major section - hills and valleys
    (70.0, -2.0, 40.0),   # Valley
    (95.0, 4.0, 55.0),    # Big hill
    (120.0, 1.0, 70.0),   # Plateau
    (145.0, -1.0, 85.0),  # Downhill
    
    # Second section - curves and turns
    (170.0, 0.0, 100.0),  # Straight section
    (195.0, 3.0, 115.0),  # Turn and climb
    (220.0, 0.0, 130.0),  # Level section
    (245.0, -2.0, 145.0), # Downhill turn
    
    # Third section - more hills
    (270.0, 0.0, 160.0),  # Valley
    (295.0, 5.0, 175.0),  # Major hill
    (320.0, 2.0, 190.0),  # Plateau
    (345.0, 0.0, 205.0),  # Level section
    
    # Fourth section - return journey
    (320.0, -1.0, 220.0), # Turn back
    (295.0, 0.0, 235.0),  # Straight
    (270.0, 3.0, 250.0),  # Hill
    (245.0, 0.0, 265.0),  # Level
    
    # Fifth section - final stretch
    (220.0, -2.0, 280.0), # Downhill
    (195.0, 0.0, 295.0),  # Valley
    (170.0, 2.0, 310.0),  # Small hill
    (145.0, 0.0, 325.0),  # Level
    
    # Sixth section - approaching end
    (120.0, -1.0, 340.0), # Downhill
    (95.0, 0.0, 355.0),   # Level
    (70.0, 1.0, 370.0),   # Small rise
    (45.0, 0.0, 385.0),   # Level
    
    # Final section - return to start area
    (20.0, -1.0, 400.0),  # Final downhill
    (0.0, 0.0, 415.0),    # Near start
    (-15.0, 0.0, 430.0),  # Extend past start
    (-30.0, 0.0, 445.0),  # Final point
]

def catmull_rom_point(p0, p1, p2, p3, t):
    """
    Compute a point on a Catmull-Rom spline segment.

    Args:
        p0, p1, p2, p3: Control points as numpy arrays or tuples
        t: Parameter in [0, 1] where 0 = p1, 1 = p2

    Returns:
        Point on the curve as numpy array
    """
    # Convert to numpy arrays for consistent math
    p0 = np.array(p0, dtype=float)
    p1 = np.array(p1, dtype=float)
    p2 = np.array(p2, dtype=float)
    p3 = np.array(p3, dtype=float)

    # Catmull-Rom basis matrix calculation
    t2 = t * t
    t3 = t2 * t

    # Catmull-Rom spline formula
    point = 0.5 * (
        (2 * p1) +
        (-p0 + p2) * t +
        (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
        (-p0 + 3 * p1 - 3 * p2 + p3) * t3
    )

    return point

def get_point(control_points, t):
    """
    Get a point on the roller coaster track curve.

    Args:
        control_points: List of 3D control points (x, y, z)
        t: Parameter in [0, 1) where the track loops

    Returns:
        3D position as numpy array (x, y, z)

    Note:
        Uses Catmull-Rom spline interpolation for smooth curves.
        The track is a closed loop, so t wraps around.
    """
    pts = control_points
    n = len(pts)

    if n < 4:
        # Not enough points for spline, return first point
        return np.array(pts[0], dtype=float)

    # Handle closed loop by wrapping around the endpoints
    # For a closed curve, we need to extend the control points
    if n >= 4:
        # Extend the control points for seamless looping
        extended_points = pts + pts[:3]  # Add first 3 points to the end
    else:
        extended_points = pts

    n_extended = len(extended_points)

    # Scale t to number of segments (n-3 segments in original, but with extension)
    # We have (n_extended-3) segments
    seg_count = n_extended - 3
    t_scaled = (t % 1.0) * seg_count
    seg_index = int(t_scaled)
    local_t = t_scaled - seg_index

    # Clamp segment index to valid range
    seg_index = min(seg_index, seg_count - 1)

    # Get the four control points for this segment
    i = seg_index
    p0 = extended_points[i]
    p1 = extended_points[i + 1]
    p2 = extended_points[i + 2]
    p3 = extended_points[i + 3]

    # Compute the point on the spline
    return catmull_rom_point(p0, p1, p2, p3, local_t)

def get_tangent(control_points, t, delta_t=1e-3):
    """
    Compute the tangent (forward direction) at a point on the curve.

    Args:
        control_points: List of 3D control points
        t: Parameter in [0, 1)
        delta_t: Small step for numerical differentiation

    Returns:
        Normalized tangent vector as numpy array
    """
    p1 = get_point(control_points, t)
    p2 = get_point(control_points, (t + delta_t) % 1.0)

    tangent = p2 - p1
    length = np.linalg.norm(tangent)

    if length == 0:
        # Fallback tangent if points are identical
        return np.array([1.0, 0.0, 0.0])

    return tangent / length

def get_curvature(control_points, t, delta_t=1e-3):
    """
    Compute the curvature at a point on the curve.

    Args:
        control_points: List of 3D control points
        t: Parameter in [0, 1)
        delta_t: Small step for numerical differentiation

    Returns:
        Curvature value (higher = sharper turn)
    """
    # Get first and second derivatives numerically
    p1 = get_point(control_points, t)
    p2 = get_point(control_points, (t + delta_t) % 1.0)
    p3 = get_point(control_points, (t + 2 * delta_t) % 1.0)

    # First derivative (tangent)
    v1 = (p2 - p1) / delta_t

    # Second derivative
    v2 = (p3 - 2 * p2 + p1) / (delta_t * delta_t)

    # Cross product magnitude / speed^3
    cross_mag = np.linalg.norm(np.cross(v1, v2))
    speed = np.linalg.norm(v1)

    if speed == 0:
        return 0.0

    return cross_mag / (speed * speed * speed)

def get_total_length(control_points, samples=1000):
    """
    Approximate the total length of the curve.

    Args:
        control_points: List of 3D control points
        samples: Number of sample points for approximation

    Returns:
        Approximate curve length
    """
    total_length = 0.0
    prev_point = get_point(control_points, 0.0)

    for i in range(1, samples + 1):
        t = i / samples
        curr_point = get_point(control_points, t)
        total_length += np.linalg.norm(curr_point - prev_point)
        prev_point = curr_point

    return total_length
















