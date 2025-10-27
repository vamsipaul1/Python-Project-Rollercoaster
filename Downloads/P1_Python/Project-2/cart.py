"""
cart.py
Author: AI assistant
Purpose: Draw and orient a 3D cart (roller coaster car) on the track
"""

import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *

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

def rotation_matrix_from_vectors(forward, up):
    """
    Create a rotation matrix from forward and up vectors.

    Args:
        forward: Forward direction vector
        up: Up direction vector

    Returns:
        4x4 rotation matrix as numpy array
    """
    forward = normalize_vector(forward)
    up = normalize_vector(up)

    # Compute right vector
    right = normalize_vector(cross_product(forward, up))
    # Re-orthogonalize up vector
    up = normalize_vector(cross_product(right, forward))

    # Create rotation matrix (column-major order for OpenGL)
    rotation = np.identity(4, dtype=float)
    rotation[0, 0:3] = right
    rotation[1, 0:3] = up
    rotation[2, 0:3] = forward

    return rotation

def draw_cart_at(position, forward, up=None, size=0.3, color=None):
    """
    Draw a 3D cart (cube) at the specified position and orientation.

    Args:
        position: Cart position as (x, y, z)
        forward: Forward direction vector
        up: Up direction vector (default: [0, 1, 0])
        size: Size of the cart (width/height/depth)
        color: RGB color tuple (default: red cart)

    The cart is oriented to face the forward direction and is slightly
    tilted based on the track curvature for realistic appearance.
    """
    if up is None:
        up = np.array([0.0, 1.0, 0.0])

    pos = np.array(position, dtype=float)
    forward = normalize_vector(forward)
    up = normalize_vector(up)

    # Default cart color (red)
    if color is None:
        color = (1.0, 0.2, 0.2)  # Red cart

    # Set cart color
    glColor3f(color[0], color[1], color[2])

    # Create rotation matrix
    rotation = rotation_matrix_from_vectors(forward, up)

    # Draw the cart using transformations
    glPushMatrix()

    # Translate to position
    glTranslatef(float(pos[0]), float(pos[1]), float(pos[2]))

    # Apply rotation (OpenGL expects column-major matrix)
    glMultMatrixf(rotation.T.flatten().tolist())

    # Draw main cart body (slightly elongated cube)
    glPushMatrix()
    glScalef(size * 1.5, size * 0.8, size)  # Elongated along track direction
    glutSolidCube(1.0)
    glPopMatrix()

    # Draw cart details - small wheels or supports
    glColor3f(0.3, 0.3, 0.3)  # Dark gray for details

    # Front wheels/supports
    glPushMatrix()
    glTranslatef(size * 0.6, -size * 0.5, size * 0.4)
    glScalef(size * 0.3, size * 0.2, size * 0.3)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(size * 0.6, -size * 0.5, -size * 0.4)
    glScalef(size * 0.3, size * 0.2, size * 0.3)
    glutSolidCube(1.0)
    glPopMatrix()

    # Back wheels/supports
    glPushMatrix()
    glTranslatef(-size * 0.6, -size * 0.5, size * 0.4)
    glScalef(size * 0.3, size * 0.2, size * 0.3)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-size * 0.6, -size * 0.5, -size * 0.4)
    glScalef(size * 0.3, size * 0.2, size * 0.3)
    glutSolidCube(1.0)
    glPopMatrix()

    # Add a small seat or passenger area
    glColor3f(0.8, 0.6, 0.2)  # Brown/orange for seat
    glPushMatrix()
    glTranslatef(0.0, size * 0.3, 0.0)
    glScalef(size * 0.8, size * 0.2, size * 0.8)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()

def draw_simple_cart_at(position, forward, up=None, size=0.3):
    """
    Draw a simplified cart (just a colored cube) for better performance.

    Args:
        position: Cart position as (x, y, z)
        forward: Forward direction vector
        up: Up direction vector (default: [0, 1, 0])
        size: Size of the cart cube
    """
    if up is None:
        up = np.array([0.0, 1.0, 0.0])

    pos = np.array(position, dtype=float)
    forward = normalize_vector(forward)
    up = normalize_vector(up)

    # Create rotation matrix
    rotation = rotation_matrix_from_vectors(forward, up)

    # Draw simple cart
    glPushMatrix()

    # Translate to position
    glTranslatef(float(pos[0]), float(pos[1]), float(pos[2]))

    # Apply rotation
    glMultMatrixf(rotation.T.flatten().tolist())

    # Draw simple cube cart
    glColor3f(1.0, 0.3, 0.3)  # Red cart
    glutSolidCube(size)

    glPopMatrix()

def draw_cart_wireframe_at(position, forward, up=None, size=0.3):
    """
    Draw a wireframe cart for debugging purposes.

    Args:
        position: Cart position as (x, y, z)
        forward: Forward direction vector
        up: Up direction vector (default: [0, 1, 0])
        size: Size of the cart
    """
    if up is None:
        up = np.array([0.0, 1.0, 0.0])

    pos = np.array(position, dtype=float)
    forward = normalize_vector(forward)
    up = normalize_vector(up)

    # Create rotation matrix
    rotation = rotation_matrix_from_vectors(forward, up)

    # Draw wireframe cart
    glPushMatrix()

    # Translate to position
    glTranslatef(float(pos[0]), float(pos[1]), float(pos[2]))

    # Apply rotation
    glMultMatrixf(rotation.T.flatten().tolist())

    # Draw wireframe cube
    glColor3f(0.0, 1.0, 0.0)  # Green wireframe
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glutSolidCube(size)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glPopMatrix()

def get_cart_bounds(position, size=0.3):
    """
    Get the bounding box of the cart for collision detection.

    Args:
        position: Cart position as (x, y, z)
        size: Cart size

    Returns:
        Dictionary with min/max bounds
    """
    pos = np.array(position, dtype=float)
    half_size = size / 2.0

    return {
        'min': pos - half_size,
        'max': pos + half_size,
        'center': pos
    }










