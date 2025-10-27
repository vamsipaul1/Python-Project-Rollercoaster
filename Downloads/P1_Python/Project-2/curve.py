"""
curve.py
Author: AI assistant
Purpose: Spline curve utilities for roller coaster track using Catmull-Rom interpolation
"""

import numpy as np

# Default control points for the roller coaster track
# These form a closed loop track with hills and curves
control_points = [
    (0.0, 0.0, 0.0),      # Start point
    (5.0, 0.0, 2.0),      # First curve up
    (10.0, 2.0, 5.0),     # Hill top
    (15.0, 0.0, 8.0),     # Downhill
    (20.0, -1.0, 5.0),    # Valley
    (25.0, 1.0, 2.0),     # Back uphill
    (30.0, 3.0, 0.0),     # High point
    (35.0, 0.0, -3.0),    # Sharp turn
    (40.0, -2.0, 0.0),    # Low point
    (35.0, 0.0, 3.0),     # Turn back
    (30.0, 1.0, 0.0),     # Approach start
    (25.0, 0.0, -2.0),    # Final curve
    (20.0, 0.0, 0.0),     # Back to area near start
    (15.0, 0.0, 2.0),     # Curve around
    (10.0, 0.0, 0.0),     # Near start
    (5.0, 0.0, -1.0),     # Final approach
    (0.0, 0.0, 0.0)       # Back to start (closed loop)
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
















