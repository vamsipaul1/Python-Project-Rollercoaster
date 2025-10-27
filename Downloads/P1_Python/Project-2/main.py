"""
main.py
Author: AI assistant
Purpose: Entry point for Intermediate Submission 2 - Roller Coaster Simulation
Integrates curve, cart, and camera systems for a complete roller coaster experience.
"""

import sys
import time
import numpy as np

# Import local modules
from curve import get_point, control_points
from cart import draw_cart_at
from camera import apply_camera, get_camera_description

# OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Configuration constants
DEBUG = False
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
DEFAULT_SPEED = 0.08
MAX_SPEED = 0.5
MIN_SPEED = 0.0

# Animation and camera state
t_param = 0.0                    # Current position on track (0.0 to 1.0)
speed = DEFAULT_SPEED           # Cart speed along track
paused = False                  # Animation pause state
last_time = None               # For delta time calculation
camera_mode = 0                # 0 = third-person, 1 = first-person
show_track = True              # Whether to display track visualization
show_cart_info = False         # Whether to show debug info

def debug_print(*args):
    """Print debug messages if DEBUG is enabled."""
    if DEBUG:
        print(*args)

def init_opengl():
    """Initialize OpenGL settings."""
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.5, 0.7, 1.0, 1.0)  # Sky blue background
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    # Enable lighting for better 3D appearance
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Set light position and properties
    glLightfv(GL_LIGHT0, GL_POSITION, [10.0, 10.0, 10.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])

    # Enable color material for simple coloring
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

def reshape_window(width, height):
    """Handle window resize events."""
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH, WINDOW_HEIGHT = width, height

    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, width / float(height) if height != 0 else 1.0, 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW)

def get_cart_forward(t, delta_t=1e-3):
    """
    Compute the forward direction vector of the cart at parameter t.

    Args:
        t: Parameter along track (0.0 to 1.0)
        delta_t: Small step for numerical differentiation

    Returns:
        Normalized forward vector as numpy array
    """
    p1 = np.array(get_point(control_points, t), dtype=float)
    p2 = np.array(get_point(control_points, (t + delta_t) % 1.0), dtype=float)

    forward = p2 - p1
    length = np.linalg.norm(forward)

    if length == 0:
        # Fallback if points are identical
        return np.array([1.0, 0.0, 0.0])

    return forward / length

def draw_environment():
    """Draw the environment (ground, sky, etc.)."""
    # Draw ground plane
    glDisable(GL_LIGHTING)
    glColor3f(0.3, 0.8, 0.3)  # Green ground
    glBegin(GL_QUADS)
    glVertex3f(-50.0, -3.0, -50.0)
    glVertex3f(50.0, -3.0, -50.0)
    glVertex3f(50.0, -3.0, 50.0)
    glVertex3f(-50.0, -3.0, 50.0)
    glEnd()
    glEnable(GL_LIGHTING)

    # Draw some simple environment objects (trees, buildings, etc.)
    draw_simple_trees()
    draw_simple_buildings()

def draw_simple_trees():
    """Draw simple tree-like objects in the environment."""
    glDisable(GL_LIGHTING)

    # Tree positions scattered around the track
    tree_positions = [
        (8, -2, 3), (12, -2, 7), (18, -2, 10), (22, -2, 3),
        (28, -2, -2), (32, -2, 2), (38, -2, -5), (42, -2, 2)
    ]

    for pos in tree_positions:
        # Tree trunk (brown cylinder)
        glColor3f(0.6, 0.3, 0.1)
        glPushMatrix()
        glTranslatef(pos[0], pos[1], pos[2])
        glScalef(0.5, 2.0, 0.5)
        glutSolidCube(1.0)
        glPopMatrix()

        # Tree leaves (green sphere)
        glColor3f(0.2, 0.8, 0.2)
        glPushMatrix()
        glTranslatef(pos[0], pos[1] + 2.5, pos[2])
        glutSolidSphere(1.5, 8, 8)
        glPopMatrix()

    glEnable(GL_LIGHTING)

def draw_simple_buildings():
    """Draw simple building-like objects in the environment."""
    glDisable(GL_LIGHTING)

    # Building positions
    building_positions = [
        (-5, -2, -10), (-8, -2, 8), (45, -2, -8), (48, -2, 5)
    ]

    for pos in building_positions:
        # Building base
        glColor3f(0.7, 0.7, 0.8)
        glPushMatrix()
        glTranslatef(pos[0], pos[1], pos[2])
        glScalef(3.0, 4.0, 3.0)
        glutSolidCube(1.0)
        glPopMatrix()

        # Building roof
        glColor3f(0.8, 0.4, 0.2)
        glPushMatrix()
        glTranslatef(pos[0], pos[1] + 2.5, pos[2])
        glScalef(3.5, 0.5, 3.5)
        glutSolidCube(1.0)
        glPopMatrix()

    glEnable(GL_LIGHTING)

def draw_track_visualization(points, samples=200):
    """Draw the track as a line strip for visualization."""
    if not show_track:
        return

    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_LIGHTING)

    glBegin(GL_LINE_STRIP)
    glColor3f(0.8, 0.8, 0.8)  # Light gray track

    for i in range(samples + 1):
        t = i / float(samples)
        point = get_point(points, t)
        glVertex3f(float(point[0]), float(point[1]), float(point[2]))

    glEnd()
    glPopAttrib()

def draw_ui_text():
    """Draw on-screen UI text with controls and info."""
    if not show_cart_info:
        return

    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1.0, 1.0, 1.0)  # White text
    glRasterPos2f(10, WINDOW_HEIGHT - 30)

    # Display current info
    info_text = f"Speed: {speed:.3f} | Camera: {get_camera_description(camera_mode)} | Paused: {paused}"
    for char in info_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

    # Display controls reminder
    glRasterPos2f(10, 20)
    controls_text = "W/S: Speed | Space: Pause | C: Camera | I: Info | T: Track | Esc: Quit"
    for char in controls_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(char))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glPopAttrib()

def display():
    """Main display function called by GLUT."""
    global t_param, last_time

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Calculate delta time
    current_time = time.time()
    if last_time is None:
        delta_time = 1.0 / 60.0  # Default 60 FPS
    else:
        delta_time = current_time - last_time
    last_time = current_time

    # Update cart position if not paused
    if not paused:
        t_param = (t_param + speed * delta_time) % 1.0

    # Get current cart state
    cart_position = get_point(control_points, t_param)
    cart_forward = get_cart_forward(t_param)

    # Apply camera transformation
    apply_camera(
        mode=camera_mode,
        cart_position=cart_position,
        cart_forward=cart_forward,
        follow_distance=4.0,
        height_offset=2.0,
        lookahead=1.5,
        driver_height=0.3
    )

    # Draw environment
    draw_environment()

    # Draw track visualization
    draw_track_visualization(control_points)

    # Draw the cart
    draw_cart_at(
        position=cart_position,
        forward=cart_forward,
        size=0.4,
        color=(1.0, 0.3, 0.3)  # Red cart
    )

    # Draw UI
    draw_ui_text()

    glutSwapBuffers()

def keyboard_handler(key, x, y):
    """Handle keyboard input."""
    global speed, paused, camera_mode, show_cart_info, show_track

    key = key.decode('utf-8').lower()

    if key == 'w':
        speed = min(MAX_SPEED, speed + 0.02)
        debug_print(f"Speed increased to {speed}")
    elif key == 's':
        speed = max(MIN_SPEED, speed - 0.02)
        debug_print(f"Speed decreased to {speed}")
    elif key == ' ':
        paused = not paused
        debug_print(f"Animation {'paused' if paused else 'resumed'}")
    elif key == 'c':
        camera_mode = 1 - camera_mode
        debug_print(f"Camera mode: {get_camera_description(camera_mode)}")
    elif key == 'i':
        show_cart_info = not show_cart_info
        debug_print(f"Info display: {'on' if show_cart_info else 'off'}")
    elif key == 't':
        show_track = not show_track
        debug_print(f"Track display: {'on' if show_track else 'off'}")
    elif key == '\x1b' or key == 'q':  # Escape or Q to quit
        debug_print("Exiting...")
        sys.exit(0)

def idle():
    """Idle function for smooth animation."""
    glutPostRedisplay()

def demo_mode():
    """Run simulation in demo mode without graphics (for testing)."""
    # Import camera module for demo
    from camera import get_camera_info

    print("=" * 60)
    print("ROLLER COASTER SIMULATION - DEMO MODE")
    print("=" * 60)
    print("Testing core simulation logic without graphics...")
    print()

    # Test the simulation loop
    t = 0.0
    speed = DEFAULT_SPEED

    for i in range(50):  # Simulate 50 frames
        # Get cart position
        pos = get_point(control_points, t)
        forward = get_cart_forward(t)

        # Get camera info
        cam_info = get_camera_info(0, pos, forward)

        print(f"Frame {i+1:2d}: t={t:.3f}, Pos={pos}, Speed={speed:.3f}")

        # Update parameters
        t = (t + speed * 0.016) % 1.0  # 60 FPS simulation

        if i % 10 == 0:  # Change speed every 10 frames for demo
            speed = min(MAX_SPEED, speed + 0.01)

    print()
    print("Demo completed! All simulation systems working correctly.")
    print("To run with graphics, install freeglut and run: python main.py")
    print("=" * 60)

def run():
    """Initialize and start the OpenGL application."""
    # Check if GLUT is available
    try:
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        glutCreateWindow(b"Roller Coaster - Intermediate Submission 2")
    except Exception as e:
        print("=" * 60)
        print("ERROR: GLUT (OpenGL Utility Toolkit) is not available!")
        print("=" * 60)
        print()
        print("SOLUTION FOR WINDOWS:")
        print("1. Download freeglut from: http://freeglut.sourceforge.net/")
        print("2. Install freeglut and copy freeglut.dll to your System32 folder")
        print("3. Or add freeglut.dll to your Python installation directory")
        print()
        print("ALTERNATIVE: Use the --demo flag to run without graphics:")
        print("   python main.py --demo")
        print("=" * 60)
        sys.exit(1)

    # Initialize OpenGL
    init_opengl()

    # Set up GLUT callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape_window)
    glutKeyboardFunc(keyboard_handler)
    glutIdleFunc(idle)

    # Print startup information
    print("=" * 60)
    print("Roller Coaster Simulation - Intermediate Submission 2")
    print("=" * 60)
    print(f"PyOpenGL version: {glGetString(GL_VERSION)}")
    print(f"Control points: {len(control_points)}")
    print(f"Track length: ~{len(control_points) * 5} units")
    print(f"Initial speed: {speed}")
    print()
    print("Controls:")
    print("  W         - Increase speed")
    print("  S         - Decrease speed")
    print("  Space     - Pause/Resume animation")
    print("  C         - Toggle camera mode (3rd/1st person)")
    print("  I         - Toggle info display")
    print("  T         - Toggle track visualization")
    print("  Esc/Q     - Quit")
    print()
    print("Starting simulation...")
    print("=" * 60)

    # Start the main loop
    glutMainLoop()

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] in ['--demo', '-d', 'demo']:
        demo_mode()
    else:
        try:
            run()
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user.")
            sys.exit(0)
        except Exception as e:
            print(f"\nError running simulation: {e}")
            print("\nTry running in demo mode: python main.py --demo")
            sys.exit(1)





