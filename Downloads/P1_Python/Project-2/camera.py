"""
camera.py
Author: AI assistant
Purpose: Camera utilities for roller coaster project (third-person & first-person modes)
"""

import numpy as np
from OpenGL.GLU import gluLookAt

def normalize_vector(v):
    """
    Normalize a 3D vector.

    Args:
        v: Vector as list, tuple, or numpy array

    Returns:
        Normalized vector as numpy array
    """
    v = np.array(v, dtype=float)
    norm = np.linalg.norm(v)
    return v / norm if norm != 0 else np.array([0.0, 0.0, 1.0])

def cross_product(a, b):
    """
    Compute cross product of two 3D vectors.

    Args:
        a, b: 3D vectors

    Returns:
        Cross product as numpy array
    """
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    return np.cross(a, b)

def apply_camera(mode, cart_position, cart_forward, cart_up=None,
                 follow_distance=3.0, height_offset=1.5, lookahead=1.0,
                 driver_height=0.3, damping=1.0):
    """
    Apply camera transformation using gluLookAt.

    Args:
        mode: 0 = third-person follow camera, 1 = first-person camera
        cart_position: Current cart position as (x, y, z)
        cart_forward: Forward direction vector of the cart
        cart_up: Up direction vector (default: [0, 1, 0])
        follow_distance: Distance behind cart in third-person mode
        height_offset: Height above cart in third-person mode
        lookahead: How far ahead to look in both modes
        driver_height: Eye height in first-person mode
        damping: Camera smoothing factor (not implemented yet)

    The camera smoothly follows the cart's movement and orientation.
    """
    # Convert inputs to numpy arrays
    pos = np.array(cart_position, dtype=float)
    forward = normalize_vector(cart_forward)

    # Default up vector if not provided
    if cart_up is None:
        up = np.array([0.0, 1.0, 0.0], dtype=float)
    else:
        up = normalize_vector(cart_up)

    # Compute right vector for coordinate system
    right = normalize_vector(cross_product(forward, up))
    up = normalize_vector(cross_product(right, forward))  # Re-orthogonalize

    eye = None
    center = None

    if mode == 0:  # Third-person follow camera
        # Position camera behind and above the cart
        eye = (pos - forward * follow_distance + up * height_offset)

        # Look ahead of the cart's current position
        center = pos + forward * lookahead

    elif mode == 1:  # First-person camera (inside cart)
        # Position camera at driver's eye level inside the cart
        eye = pos + up * driver_height

        # Look ahead from the driver's perspective
        center = pos + forward * lookahead

    else:
        # Fallback to third-person
        eye = pos - forward * follow_distance + up * height_offset
        center = pos + forward * lookahead

    # Apply the camera transformation
    gluLookAt(
        float(eye[0]), float(eye[1]), float(eye[2]),      # Camera position
        float(center[0]), float(center[1]), float(center[2]),  # Look at point
        float(up[0]), float(up[1]), float(up[2])           # Up vector
    )

def apply_camera_smooth(mode, cart_position, cart_forward, cart_up=None,
                       follow_distance=3.0, height_offset=1.5, lookahead=1.0,
                       driver_height=0.3, smoothness=0.1):
    """
    Apply camera with optional smoothing (for future enhancement).

    Args:
        smoothness: Camera smoothing factor (0 = no smoothing, 1 = very smooth)

    Note:
        Smoothing is not fully implemented in this version but the interface
        is ready for future enhancement with interpolation.
    """
    apply_camera(mode, cart_position, cart_forward, cart_up,
                follow_distance, height_offset, lookahead, driver_height)

def get_camera_info(mode, cart_position, cart_forward, cart_up=None):
    """
    Get camera parameters without applying transformation (for debugging).

    Args:
        Same as apply_camera

    Returns:
        Dictionary with camera parameters
    """
    pos = np.array(cart_position, dtype=float)
    forward = normalize_vector(cart_forward)

    if cart_up is None:
        up = np.array([0.0, 1.0, 0.0], dtype=float)
    else:
        up = normalize_vector(cart_up)

    right = normalize_vector(cross_product(forward, up))

    if mode == 0:  # Third-person
        eye = pos - forward * 3.0 + up * 1.5
        center = pos + forward * 1.0
    else:  # First-person
        eye = pos + up * 0.3
        center = pos + forward * 1.0

    return {
        'mode': mode,
        'eye': eye,
        'center': center,
        'up': up,
        'forward': forward,
        'right': right
    }

def toggle_camera_mode(current_mode):
    """
    Toggle between camera modes.

    Args:
        current_mode: Current camera mode (0 or 1)

    Returns:
        New camera mode
    """
    return 1 - current_mode

def get_camera_description(mode):
    """
    Get human-readable description of camera mode.

    Args:
        mode: Camera mode (0 or 1)

    Returns:
        Description string
    """
    if mode == 0:
        return "Third-person (behind cart)"
    else:
        return "First-person (inside cart)"
















