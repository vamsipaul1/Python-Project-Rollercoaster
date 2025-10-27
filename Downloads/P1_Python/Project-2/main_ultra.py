"""
main_ultra.py - Ultra Professional Roller Coaster with Smooth Camera & Enhanced Graphics
Author: AI assistant
Purpose: Ultra-realistic roller coaster with cinematic camera work and premium graphics

ULTRA FEATURES:
- Smooth, realistic camera movements with interpolation
- Multiple cinematic viewpoints
- Enhanced tree and environment graphics
- Professional camera transitions
- Realistic physics-based camera following
- Premium visual quality
"""

import sys
import time
import math
import numpy as np

# Import local modules
from curve import get_point, control_points, get_tangent
from cart import normalize_vector, cross_product
from camera import get_camera_info

# OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Configuration constants
DEBUG = False
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
DEFAULT_SPEED = 0.05
MAX_SPEED = 0.3
MIN_SPEED = 0.0

# Animation and camera state
t_param = 0.0
speed = DEFAULT_SPEED
paused = False
last_time = None
camera_mode = 0  # 0=follow, 1=first-person, 2=cinematic, 3=orbit, 4=flyby
show_track = True
show_cart_info = True
show_environment = True
fog_enabled = True
lighting_enhanced = True

# Camera smoothing and interpolation
camera_position = np.array([0.0, 5.0, 10.0])
camera_target = np.array([0.0, 0.0, 0.0])
camera_up = np.array([0.0, 1.0, 0.0])
camera_smooth_factor = 0.15  # Lower = smoother but more lag

# Visual enhancement settings
terrain_size = 150.0
track_thickness = 0.12
cart_scale = 0.6
lighting_intensity = 1.2

def debug_print(*args):
    """Print debug messages if DEBUG is enabled."""
    if DEBUG:
        print(*args)

def init_ultra_opengl():
    """Initialize OpenGL with ultra-quality settings."""
    # Basic OpenGL setup
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClearColor(0.3, 0.6, 0.9, 1.0)  # Beautiful sky blue
    
    # Ultra-quality rendering settings
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)
    
    # Premium shading
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)
    glEnable(GL_AUTO_NORMAL)
    
    # Ultra lighting system
    if lighting_enhanced:
        setup_ultra_lighting()
    
    # Premium fog
    if fog_enabled:
        setup_premium_fog()
    
    # Anti-aliasing and smoothing
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POLYGON_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    
    # Premium blending
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def setup_ultra_lighting():
    """Set up ultra-quality lighting with multiple sources."""
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Main sun light (warm, directional)
    glEnable(GL_LIGHT0)
    sun_position = [30.0, 50.0, 30.0, 1.0]
    sun_ambient = [0.25, 0.25, 0.35, 1.0]
    sun_diffuse = [1.0, 0.95, 0.8, 1.0]  # Warm sunlight
    sun_specular = [1.0, 1.0, 0.9, 1.0]
    
    glLightfv(GL_LIGHT0, GL_POSITION, sun_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, sun_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, sun_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, sun_specular)
    
    # Sky light (cool, soft)
    glEnable(GL_LIGHT1)
    sky_position = [-20.0, 40.0, -20.0, 1.0]
    sky_ambient = [0.15, 0.2, 0.3, 1.0]
    sky_diffuse = [0.3, 0.4, 0.6, 1.0]  # Cool sky light
    
    glLightfv(GL_LIGHT1, GL_POSITION, sky_position)
    glLightfv(GL_LIGHT1, GL_AMBIENT, sky_ambient)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, sky_diffuse)
    
    # Bounce light (subtle fill)
    glEnable(GL_LIGHT2)
    bounce_position = [0.0, 10.0, -40.0, 1.0]
    bounce_ambient = [0.1, 0.15, 0.2, 1.0]
    bounce_diffuse = [0.2, 0.25, 0.3, 1.0]
    
    glLightfv(GL_LIGHT2, GL_POSITION, bounce_position)
    glLightfv(GL_LIGHT2, GL_AMBIENT, bounce_ambient)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, bounce_diffuse)
    
    # Global ambient
    global_ambient = [0.15, 0.18, 0.25, 1.0]
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, global_ambient)

def setup_premium_fog():
    """Set up premium atmospheric fog."""
    glEnable(GL_FOG)
    fog_color = [0.3, 0.6, 0.9, 1.0]  # Match sky
    glFogfv(GL_FOG_COLOR, fog_color)
    glFogf(GL_FOG_DENSITY, 0.006)  # Very light fog
    glFogi(GL_FOG_MODE, GL_EXP2)
    glHint(GL_FOG_HINT, GL_NICEST)

def smooth_camera_interpolation(target_pos, target_look, target_up, dt):
    """Smooth camera movement using interpolation."""
    global camera_position, camera_target, camera_up
    
    # Smooth interpolation factor based on frame time
    smooth_factor = min(camera_smooth_factor / dt, 1.0) if dt > 0 else 1.0
    
    # Interpolate position
    camera_position = camera_position + (target_pos - camera_position) * smooth_factor
    camera_target = camera_target + (target_look - camera_target) * smooth_factor
    camera_up = camera_up + (target_up - camera_up) * smooth_factor
    
    # Normalize up vector
    camera_up = normalize_vector(camera_up)

def apply_ultra_camera(cart_pos, cart_forward, current_time, dt):
    """Apply ultra-smooth camera with multiple modes."""
    global camera_position, camera_target, camera_up
    
    cart_pos = np.array(cart_pos, dtype=float)
    cart_forward = normalize_vector(cart_forward)
    cart_up = np.array([0.0, 1.0, 0.0])
    cart_right = normalize_vector(cross_product(cart_forward, cart_up))
    
    if camera_mode == 0:  # Smooth follow camera
        # Position behind and above cart
        offset_distance = 6.0
        offset_height = 3.0
        lookahead = 2.5
        
        target_pos = cart_pos - cart_forward * offset_distance + cart_up * offset_height
        target_look = cart_pos + cart_forward * lookahead
        target_up = cart_up
        
    elif camera_mode == 1:  # First-person (inside cart)
        target_pos = cart_pos + cart_up * 0.5
        target_look = cart_pos + cart_forward * 3.0
        target_up = cart_up
        
    elif camera_mode == 2:  # Cinematic tracking
        # Dynamic camera that moves around the action
        orbit_radius = 8.0
        orbit_height = 4.0
        orbit_speed = 0.4
        
        angle = current_time * orbit_speed + t_param * 2.0
        
        target_pos = cart_pos + np.array([
            orbit_radius * math.cos(angle),
            orbit_height + 2.0 * math.sin(angle * 0.7),
            orbit_radius * math.sin(angle)
        ])
        target_look = cart_pos + cart_forward * 1.0
        target_up = cart_up
        
    elif camera_mode == 3:  # Orbit camera
        # Smooth orbital camera
        orbit_radius = 12.0
        orbit_height = 6.0
        orbit_speed = 0.2
        
        angle = current_time * orbit_speed
        
        target_pos = cart_pos + np.array([
            orbit_radius * math.cos(angle),
            orbit_height,
            orbit_radius * math.sin(angle)
        ])
        target_look = cart_pos
        target_up = cart_up
        
    elif camera_mode == 4:  # Flyby camera
        # Camera that flies by the track at different angles
        flyby_distance = 15.0
        flyby_height = 8.0
        flyby_speed = 0.3
        
        angle = current_time * flyby_speed + t_param * 3.0
        
        target_pos = cart_pos + np.array([
            flyby_distance * math.cos(angle + math.pi/4),
            flyby_height + 3.0 * math.sin(angle * 0.5),
            flyby_distance * math.sin(angle + math.pi/4)
        ])
        target_look = cart_pos + cart_forward * 2.0
        target_up = cart_up
    
    else:  # Default to follow
        target_pos = cart_pos + np.array([0, 5, 10])
        target_look = cart_pos
        target_up = cart_up
    
    # Apply smooth interpolation
    smooth_camera_interpolation(target_pos, target_look, target_up, dt)
    
    # Apply the camera transformation
    gluLookAt(
        camera_position[0], camera_position[1], camera_position[2],
        camera_target[0], camera_target[1], camera_target[2],
        camera_up[0], camera_up[1], camera_up[2]
    )

def draw_ultra_terrain():
    """Draw ultra-quality terrain with detailed features."""
    if not show_environment:
        return
        
    glPushAttrib(GL_ENABLE_BIT)
    
    # Premium ground material
    ground_ambient = [0.1, 0.3, 0.1, 1.0]
    ground_diffuse = [0.2, 0.6, 0.2, 1.0]
    ground_specular = [0.1, 0.2, 0.1, 1.0]
    ground_shininess = [10.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, ground_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, ground_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, ground_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, ground_shininess)
    
    # Main terrain with subtle height variation
    glColor3f(0.15, 0.5, 0.15)
    
    # Draw terrain as triangle strips for smooth shading
    segments = 50
    for i in range(segments):
        glBegin(GL_TRIANGLE_STRIP)
        for j in range(segments + 1):
            for k in range(2):
                x = ((i + k) / float(segments) - 0.5) * terrain_size * 2
                z = (j / float(segments) - 0.5) * terrain_size * 2
                
                # Add subtle height variation
                height = -3.0 + 0.5 * math.sin(x * 0.1) * math.cos(z * 0.1)
                height += 0.2 * math.sin(x * 0.3) * math.sin(z * 0.2)
                
                # Calculate normal for smooth shading
                normal_x = -0.05 * math.cos(x * 0.1) * math.cos(z * 0.1)
                normal_z = 0.05 * math.sin(x * 0.1) * math.sin(z * 0.1)
                normal = normalize_vector([normal_x, 1.0, normal_z])
                
                glNormal3f(normal[0], normal[1], normal[2])
                glVertex3f(x, height, z)
        glEnd()
    
    # Add terrain details
    draw_ultra_terrain_details()
    
    glPopAttrib()

def draw_ultra_terrain_details():
    """Add ultra-detailed terrain features."""
    # Scattered rocks with realistic placement
    rock_positions = [
        (-25, -2.8, -20, 1.2, 0.8), (30, -2.6, 25, 1.5, 1.0), 
        (-35, -2.9, 15, 0.9, 0.6), (40, -2.7, -15, 1.8, 1.2),
        (15, -2.8, -35, 1.1, 0.9), (-20, -2.5, 35, 1.4, 1.1),
        (5, -2.9, 20, 0.7, 0.5), (-10, -2.7, -25, 1.0, 0.8)
    ]
    
    # Rock material
    rock_ambient = [0.2, 0.2, 0.25, 1.0]
    rock_diffuse = [0.4, 0.4, 0.5, 1.0]
    rock_specular = [0.1, 0.1, 0.2, 1.0]
    rock_shininess = [5.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, rock_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, rock_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, rock_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, rock_shininess)
    
    glColor3f(0.35, 0.35, 0.4)
    
    for x, y, z, size_x, size_z in rock_positions:
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(size_x, size_x * 0.6, size_z)
        glutSolidDodecahedron()
        glPopMatrix()

def draw_ultra_trees():
    """Draw ultra-realistic trees with detailed foliage."""
    tree_positions = [
        (-30, -2.5, -25, 3.5, 2.0), (35, -2.3, -30, 4.0, 2.5), 
        (-40, -2.4, 20, 3.8, 2.2), (45, -2.6, 30, 3.2, 1.8),
        (20, -2.5, -40, 3.6, 2.1), (-35, -2.7, 40, 4.2, 2.8),
        (-15, -2.6, -15, 2.8, 1.6), (25, -2.4, 35, 3.4, 2.0),
        (50, -2.8, 0, 3.0, 1.7), (-50, -2.5, 5, 3.7, 2.3)
    ]
    
    for x, y, z, height, crown_size in tree_positions:
        draw_single_ultra_tree(x, y, z, height, crown_size)

def draw_single_ultra_tree(x, y, z, height, crown_size):
    """Draw a single ultra-detailed tree."""
    # Trunk material
    trunk_ambient = [0.2, 0.1, 0.05, 1.0]
    trunk_diffuse = [0.4, 0.2, 0.1, 1.0]
    trunk_specular = [0.1, 0.05, 0.02, 1.0]
    trunk_shininess = [5.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, trunk_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, trunk_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, trunk_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, trunk_shininess)
    
    # Draw trunk
    glColor3f(0.4, 0.2, 0.1)
    glPushMatrix()
    glTranslatef(x, y + height/2, z)
    glScalef(0.3, height, 0.3)
    glutSolidCylinder(1.0, 1.0, 12, 8)
    glPopMatrix()
    
    # Foliage material
    foliage_ambient = [0.05, 0.2, 0.05, 1.0]
    foliage_diffuse = [0.1, 0.6, 0.1, 1.0]
    foliage_specular = [0.05, 0.3, 0.05, 1.0]
    foliage_shininess = [15.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, foliage_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, foliage_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, foliage_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, foliage_shininess)
    
    # Draw layered foliage for realistic look
    foliage_layers = [
        (0, 0.7, 0, 1.0),      # Main crown
        (0.2, 0.6, 0.1, 0.8),  # Side branch
        (-0.1, 0.8, -0.2, 0.7), # Top branch
        (0.1, 0.5, 0.2, 0.6),  # Lower branch
        (-0.2, 0.65, 0.1, 0.75) # Another side branch
    ]
    
    glColor3f(0.1, 0.5, 0.1)
    
    for fx, fy, fz, scale in foliage_layers:
        glPushMatrix()
        glTranslatef(x + fx * crown_size, y + height * fy, z + fz * crown_size)
        glutSolidSphere(crown_size * scale, 16, 12)
        glPopMatrix()

def draw_premium_track():
    """Draw premium 3D track with realistic materials."""
    if not show_track:
        return
        
    glPushAttrib(GL_ENABLE_BIT)
    
    # Premium track material
    track_ambient = [0.2, 0.2, 0.25, 1.0]
    track_diffuse = [0.6, 0.6, 0.7, 1.0]
    track_specular = [0.8, 0.8, 0.9, 1.0]
    track_shininess = [60.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, track_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, track_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, track_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, track_shininess)
    
    # Sample track points
    track_points = []
    num_samples = 300  # Higher resolution for smoother track
    
    for i in range(num_samples + 1):
        t = i / float(num_samples)
        point = get_point(control_points, t)
        tangent = get_tangent(control_points, t)
        track_points.append((point, tangent))
    
    # Draw dual rails with proper spacing
    glColor3f(0.6, 0.6, 0.7)
    draw_premium_rail(track_points, -track_thickness * 2)
    draw_premium_rail(track_points, track_thickness * 2)
    
    # Draw cross ties
    draw_premium_cross_ties(track_points)
    
    glPopAttrib()

def draw_premium_rail(track_points, offset):
    """Draw a premium rail with cylindrical cross-section."""
    glBegin(GL_QUAD_STRIP)
    
    for i, (point, tangent) in enumerate(track_points):
        up = np.array([0.0, 1.0, 0.0])
        right = normalize_vector(cross_product(tangent, up))
        rail_center = np.array(point) + right * offset
        
        # Create cylindrical rail
        radius = track_thickness * 0.4
        segments = 8
        
        for j in range(segments + 1):
            angle = (j / float(segments)) * 2 * math.pi
            
            local_right = right * math.cos(angle) + up * math.sin(angle)
            rail_pos = rail_center + local_right * radius
            
            glNormal3f(local_right[0], local_right[1], local_right[2])
            glVertex3f(rail_pos[0], rail_pos[1], rail_pos[2])
    
    glEnd()

def draw_premium_cross_ties(track_points):
    """Draw premium wooden cross ties."""
    # Wood material
    wood_ambient = [0.15, 0.1, 0.05, 1.0]
    wood_diffuse = [0.4, 0.25, 0.15, 1.0]
    wood_specular = [0.2, 0.15, 0.1, 1.0]
    wood_shininess = [10.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, wood_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, wood_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, wood_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, wood_shininess)
    
    glColor3f(0.4, 0.25, 0.15)
    
    # Draw ties every 8th point
    for i in range(0, len(track_points), 8):
        if i >= len(track_points):
            break
            
        point, tangent = track_points[i]
        up = np.array([0.0, 1.0, 0.0])
        right = normalize_vector(cross_product(tangent, up))
        
        glPushMatrix()
        glTranslatef(point[0], point[1] - track_thickness * 0.3, point[2])
        
        # Orient tie perpendicular to track
        tie_length = track_thickness * 6
        tie_width = track_thickness * 0.6
        tie_height = track_thickness * 0.4
        
        glScalef(tie_length, tie_height, tie_width)
        glutSolidCube(1.0)
        glPopMatrix()

def draw_premium_cart(position, forward, up=None):
    """Draw premium cart with ultra-detailed components."""
    if up is None:
        up = np.array([0.0, 1.0, 0.0])
    
    pos = np.array(position, dtype=float)
    forward = normalize_vector(forward)
    up = normalize_vector(up)
    right = normalize_vector(cross_product(forward, up))
    
    # Build transformation matrix
    transform = np.identity(4)
    transform[0:3, 0] = right
    transform[0:3, 1] = up
    transform[0:3, 2] = forward
    transform[0:3, 3] = pos
    
    glPushMatrix()
    glMultMatrixf(transform.T.flatten())
    
    # Premium cart body material
    body_ambient = [0.3, 0.05, 0.05, 1.0]
    body_diffuse = [0.8, 0.15, 0.15, 1.0]
    body_specular = [0.9, 0.4, 0.4, 1.0]
    body_shininess = [40.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, body_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, body_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, body_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, body_shininess)
    
    # Main cart body (more detailed shape)
    glColor3f(0.8, 0.15, 0.15)
    glPushMatrix()
    glScalef(cart_scale * 1.8, cart_scale * 0.9, cart_scale * 1.1)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Cart details
    draw_cart_details()
    
    glPopMatrix()

def draw_cart_details():
    """Draw detailed cart components."""
    # Seat
    glColor3f(0.5, 0.3, 0.1)
    glPushMatrix()
    glTranslatef(0, cart_scale * 0.4, 0)
    glScalef(cart_scale * 1.4, cart_scale * 0.25, cart_scale * 0.9)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Seat back
    glPushMatrix()
    glTranslatef(cart_scale * 0.5, cart_scale * 0.8, 0)
    glScalef(cart_scale * 0.2, cart_scale * 0.9, cart_scale * 0.9)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Wheels with premium material
    wheel_ambient = [0.05, 0.05, 0.05, 1.0]
    wheel_diffuse = [0.15, 0.15, 0.15, 1.0]
    wheel_specular = [0.4, 0.4, 0.4, 1.0]
    wheel_shininess = [25.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, wheel_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, wheel_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, wheel_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, wheel_shininess)
    
    glColor3f(0.15, 0.15, 0.15)
    
    wheel_positions = [
        (cart_scale * 0.7, -cart_scale * 0.7, cart_scale * 0.5),
        (cart_scale * 0.7, -cart_scale * 0.7, -cart_scale * 0.5),
        (-cart_scale * 0.7, -cart_scale * 0.7, cart_scale * 0.5),
        (-cart_scale * 0.7, -cart_scale * 0.7, -cart_scale * 0.5)
    ]
    
    for wx, wy, wz in wheel_positions:
        glPushMatrix()
        glTranslatef(wx, wy, wz)
        glutSolidTorus(0.08 * cart_scale, 0.25 * cart_scale, 12, 16)
        glPopMatrix()
    
    # Safety bar
    glColor3f(0.7, 0.7, 0.8)
    glPushMatrix()
    glTranslatef(0, cart_scale * 0.9, cart_scale * 0.4)
    glScalef(cart_scale * 1.6, cart_scale * 0.08, cart_scale * 0.08)
    glutSolidCube(1.0)
    glPopMatrix()

def get_cart_forward_ultra(t, dt=5e-4):
    """Ultra-smooth forward vector calculation."""
    p1 = np.array(get_point(control_points, t), dtype=float)
    p2 = np.array(get_point(control_points, (t + dt) % 1.0), dtype=float)
    
    forward = p2 - p1
    length = np.linalg.norm(forward)
    
    if length == 0:
        return np.array([1.0, 0.0, 0.0])
    
    return forward / length

def reshape_window(width, height):
    """Handle window resize with ultra settings."""
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH, WINDOW_HEIGHT = width, height
    
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # Ultra-wide field of view for cinematic feel
    gluPerspective(45.0, width / float(height) if height != 0 else 1.0, 0.1, 300.0)
    glMatrixMode(GL_MODELVIEW)

def display_ultra():
    """Ultra-quality display function."""
    global t_param, last_time
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Calculate delta time
    current_time = time.time()
    if last_time is None:
        delta_time = 1.0 / 60.0
    else:
        delta_time = current_time - last_time
    last_time = current_time
    
    # Update animation
    if not paused:
        t_param = (t_param + speed * delta_time) % 1.0
    
    # Get cart state
    cart_position = get_point(control_points, t_param)
    cart_forward = get_cart_forward_ultra(t_param)
    
    # Apply ultra camera
    apply_ultra_camera(cart_position, cart_forward, current_time, delta_time)
    
    # Draw all ultra elements
    draw_ultra_terrain()
    draw_premium_track()
    draw_ultra_trees()
    draw_premium_cart(cart_position, cart_forward)
    
    # Draw UI
    if show_cart_info:
        draw_ultra_ui()
    
    glutSwapBuffers()

def draw_ultra_ui():
    """Draw ultra-styled UI."""
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
    
    # Ultra-styled UI background
    glColor4f(0.0, 0.0, 0.0, 0.4)
    glBegin(GL_QUADS)
    glVertex2f(15, WINDOW_HEIGHT - 90)
    glVertex2f(500, WINDOW_HEIGHT - 90)
    glVertex2f(500, WINDOW_HEIGHT - 15)
    glVertex2f(15, WINDOW_HEIGHT - 15)
    glEnd()
    
    # UI text
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(25, WINDOW_HEIGHT - 35)
    
    camera_names = ["Follow", "First-Person", "Cinematic", "Orbit", "Flyby"]
    info_text = f"Speed: {speed:.3f} | Camera: {camera_names[camera_mode]} | {'PAUSED' if paused else 'RUNNING'}"
    
    for char in info_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
    
    glRasterPos2f(25, WINDOW_HEIGHT - 55)
    controls_text = "W/S: Speed | Space: Pause | C: Camera | 1-5: Camera Modes | F: Fog | L: Light | Esc: Quit"
    for char in controls_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(char))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glPopAttrib()

def keyboard_ultra(key, x, y):
    """Ultra keyboard handler with direct camera mode selection."""
    global speed, paused, camera_mode, show_cart_info, show_track
    global show_environment, fog_enabled, lighting_enhanced, camera_smooth_factor
    
    key = key.decode('utf-8').lower()
    
    if key == 'w':
        speed = min(MAX_SPEED, speed + 0.015)
        debug_print(f"Speed: {speed}")
    elif key == 's':
        speed = max(MIN_SPEED, speed - 0.015)
        debug_print(f"Speed: {speed}")
    elif key == ' ':
        paused = not paused
        debug_print(f"{'Paused' if paused else 'Resumed'}")
    elif key == 'c':
        camera_mode = (camera_mode + 1) % 5
        debug_print(f"Camera: {['Follow', 'First-Person', 'Cinematic', 'Orbit', 'Flyby'][camera_mode]}")
    elif key == '1':
        camera_mode = 0
        debug_print("Follow Camera")
    elif key == '2':
        camera_mode = 1
        debug_print("First-Person Camera")
    elif key == '3':
        camera_mode = 2
        debug_print("Cinematic Camera")
    elif key == '4':
        camera_mode = 3
        debug_print("Orbit Camera")
    elif key == '5':
        camera_mode = 4
        debug_print("Flyby Camera")
    elif key == 'i':
        show_cart_info = not show_cart_info
    elif key == 't':
        show_track = not show_track
    elif key == 'e':
        show_environment = not show_environment
    elif key == 'f':
        fog_enabled = not fog_enabled
        if fog_enabled:
            glEnable(GL_FOG)
        else:
            glDisable(GL_FOG)
    elif key == 'l':
        lighting_enhanced = not lighting_enhanced
        if lighting_enhanced:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
    elif key == '+' or key == '=':
        camera_smooth_factor = min(1.0, camera_smooth_factor + 0.05)
        debug_print(f"Camera smoothness: {camera_smooth_factor}")
    elif key == '-':
        camera_smooth_factor = max(0.01, camera_smooth_factor - 0.05)
        debug_print(f"Camera smoothness: {camera_smooth_factor}")
    elif key == '\x1b' or key == 'q':
        debug_print("Exiting...")
        sys.exit(0)

def idle_ultra():
    """Ultra idle function."""
    glutPostRedisplay()

def run_ultra():
    """Run the ultra-professional roller coaster simulation."""
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Ultra Professional Roller Coaster - Cinematic Experience")
    
    # Initialize ultra OpenGL
    init_ultra_opengl()
    
    # Set up callbacks
    glutDisplayFunc(display_ultra)
    glutReshapeFunc(reshape_window)
    glutKeyboardFunc(keyboard_ultra)
    glutIdleFunc(idle_ultra)
    
    # Print startup information
    print("=" * 80)
    print("ULTRA PROFESSIONAL ROLLER COASTER SIMULATION")
    print("CINEMATIC EXPERIENCE WITH SMOOTH CAMERA WORK")
    print("=" * 80)
    print("ULTRA FEATURES:")
    print("  * Smooth camera interpolation with 5 cinematic modes")
    print("  * Ultra-realistic terrain with height variation")
    print("  * Premium 3D track with cylindrical rails")
    print("  * Detailed cart with premium materials")
    print("  * Advanced 3-light lighting system")
    print("  * Ultra-detailed trees with layered foliage")
    print("  * Premium atmospheric fog")
    print("  * Anti-aliasing and smooth rendering")
    print()
    print("CAMERA MODES:")
    print("  1 - Follow Camera (smooth behind cart)")
    print("  2 - First-Person (inside cart)")
    print("  3 - Cinematic (dynamic tracking)")
    print("  4 - Orbit Camera (circular around cart)")
    print("  5 - Flyby Camera (dramatic angles)")
    print()
    print("ULTRA CONTROLS:")
    print("  W/S       - Speed control")
    print("  Space     - Pause/Resume")
    print("  C         - Cycle camera modes")
    print("  1-5       - Direct camera mode selection")
    print("  +/-       - Adjust camera smoothness")
    print("  F         - Toggle fog")
    print("  L         - Toggle lighting")
    print("  E         - Toggle environment")
    print("  Esc/Q     - Quit")
    print()
    print("Starting ultra simulation...")
    print("=" * 80)
    
    glutMainLoop()

if __name__ == "__main__":
    try:
        run_ultra()
    except KeyboardInterrupt:
        print("\nUltra simulation ended by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError in ultra simulation: {e}")
        print("Try running the basic version: python main.py")
        sys.exit(1)

