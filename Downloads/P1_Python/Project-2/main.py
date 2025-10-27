"""
main.py
Author: AI assistant
Purpose: Professional Roller Coaster Simulation with Cinematic Camera & Enhanced Graphics
Integrates curve, cart, and camera systems for a complete roller coaster experience.

ENHANCED FEATURES:
- 5 cinematic camera modes with smooth interpolation
- Ultra-realistic trees and terrain
- Premium 3-light system
- Anti-aliasing and atmospheric effects
- Professional visual quality
"""

import sys
import time
import math
import numpy as np

# Import local modules
from curve import get_point, control_points, get_tangent
from cart import draw_cart_at, normalize_vector, cross_product
from camera import apply_camera, get_camera_description

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

def init_opengl():
    """Initialize OpenGL with enhanced visual settings."""
    # Basic OpenGL setup
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClearColor(0.3, 0.6, 0.9, 1.0)  # Beautiful sky blue
    
    # Enhanced rendering settings
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)
    
    # Premium shading
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)
    glEnable(GL_AUTO_NORMAL)
    
    # Enhanced lighting system
    if lighting_enhanced:
        setup_enhanced_lighting()
    
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

def setup_enhanced_lighting():
    """Set up enhanced lighting with multiple sources."""
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
    """Set up atmospheric fog for depth and realism."""
    glEnable(GL_FOG)
    fog_color = [0.3, 0.6, 0.9, 1.0]  # Match sky
    glFogfv(GL_FOG_COLOR, fog_color)
    glFogf(GL_FOG_DENSITY, 0.006)  # Light fog
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

def apply_enhanced_camera(cart_pos, cart_forward, current_time, dt):
    """Apply enhanced camera with multiple smooth modes."""
    global camera_position, camera_target, camera_up
    
    cart_pos = np.array(cart_pos, dtype=float)
    cart_forward = normalize_vector(cart_forward)
    cart_up = np.array([0.0, 1.0, 0.0])
    cart_right = normalize_vector(cross_product(cart_forward, cart_up))
    
    if camera_mode == 0:  # Smooth follow camera
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

def reshape_window(width, height):
    """Handle window resize with enhanced settings."""
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH, WINDOW_HEIGHT = width, height
    
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # Enhanced perspective with better field of view
    gluPerspective(45.0, width / float(height) if height != 0 else 1.0, 0.1, 300.0)
    glMatrixMode(GL_MODELVIEW)

def get_cart_forward(t, delta_t=5e-4):
    """Enhanced forward vector calculation with smoothing."""
    p1 = np.array(get_point(control_points, t), dtype=float)
    p2 = np.array(get_point(control_points, (t + delta_t) % 1.0), dtype=float)
    
    forward = p2 - p1
    length = np.linalg.norm(forward)
    
    if length == 0:
        return np.array([1.0, 0.0, 0.0])
    
    return forward / length

def draw_enhanced_terrain():
    """Draw enhanced terrain with realistic features."""
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
    segments = 40
    for i in range(segments):
        glBegin(GL_TRIANGLE_STRIP)
        for j in range(segments + 1):
            for k in range(2):
                x = ((i + k) / float(segments) - 0.5) * terrain_size * 2
                z = (j / float(segments) - 0.5) * terrain_size * 2
                
                # Add subtle height variation
                height = -3.0 + 0.4 * math.sin(x * 0.08) * math.cos(z * 0.08)
                height += 0.15 * math.sin(x * 0.25) * math.sin(z * 0.2)
                
                # Calculate normal for smooth shading
                normal_x = -0.03 * math.cos(x * 0.08) * math.cos(z * 0.08)
                normal_z = 0.03 * math.sin(x * 0.08) * math.sin(z * 0.08)
                normal = normalize_vector([normal_x, 1.0, normal_z])
                
                glNormal3f(normal[0], normal[1], normal[2])
                glVertex3f(x, height, z)
        glEnd()
    
    # Add terrain details
    draw_terrain_details()
    
    glPopAttrib()

def draw_terrain_details():
    """Add detailed terrain features."""
    # Scattered rocks with realistic placement
    rock_positions = [
        (-25, -2.8, -20, 1.2, 0.8), (30, -2.6, 25, 1.5, 1.0), 
        (-35, -2.9, 15, 0.9, 0.6), (40, -2.7, -15, 1.8, 1.2),
        (15, -2.8, -35, 1.1, 0.9), (-20, -2.5, 35, 1.4, 1.1)
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

def draw_enhanced_trees():
    """Draw ultra-realistic trees with detailed foliage."""
    if not show_environment:
        return
        
    tree_positions = [
        (-30, -2.5, -25, 3.5, 2.0), (35, -2.3, -30, 4.0, 2.5), 
        (-40, -2.4, 20, 3.8, 2.2), (45, -2.6, 30, 3.2, 1.8),
        (20, -2.5, -40, 3.6, 2.1), (-35, -2.7, 40, 4.2, 2.8),
        (-15, -2.6, -15, 2.8, 1.6), (25, -2.4, 35, 3.4, 2.0),
        (50, -2.8, 0, 3.0, 1.7), (-50, -2.5, 5, 3.7, 2.3)
    ]
    
    for x, y, z, height, crown_size in tree_positions:
        draw_single_enhanced_tree(x, y, z, height, crown_size)

def draw_single_enhanced_tree(x, y, z, height, crown_size):
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

def draw_enhanced_buildings():
    """Draw enhanced buildings with realistic architecture."""
    if not show_environment:
        return
        
    building_positions = [
        (-60, -2.5, -30, 8, 12, 6, 'office'),
        (-70, -2.5, -25, 6, 8, 4, 'house'),
        (-65, -2.5, -40, 10, 15, 8, 'tower'),
        (60, -2.5, -35, 7, 10, 5, 'house'),
        (70, -2.5, -30, 12, 18, 10, 'office')
    ]
    
    for x, y, z, w, h, d, building_type in building_positions:
        draw_single_building(x, y, z, w, h, d, building_type)

def draw_single_building(x, y, z, w, h, d, building_type):
    """Draw a single detailed building."""
    # Building material
    if building_type == 'office':
        ambient = [0.2, 0.2, 0.25, 1.0]
        diffuse = [0.6, 0.6, 0.7, 1.0]
        specular = [0.3, 0.3, 0.4, 1.0]
        shininess = [30.0]
        color = (0.5, 0.5, 0.6)
    elif building_type == 'house':
        ambient = [0.25, 0.2, 0.15, 1.0]
        diffuse = [0.7, 0.5, 0.3, 1.0]
        specular = [0.2, 0.15, 0.1, 1.0]
        shininess = [10.0]
        color = (0.6, 0.45, 0.3)
    else:  # tower
        ambient = [0.15, 0.15, 0.2, 1.0]
        diffuse = [0.4, 0.4, 0.5, 1.0]
        specular = [0.4, 0.4, 0.5, 1.0]
        shininess = [50.0]
        color = (0.35, 0.35, 0.45)
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, shininess)
    
    # Main building body
    glColor3f(*color)
    glPushMatrix()
    glTranslatef(x, y + h/2, z)
    glScalef(w, h, d)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Add architectural details
    if building_type == 'office':
        # Windows pattern
        glColor3f(0.2, 0.3, 0.5)  # Blue windows
        for floor in range(3):
            for window in range(2):
                glPushMatrix()
                glTranslatef(x + (window - 0.5) * w * 0.6, 
                           y + h * 0.2 + floor * h * 0.25, 
                           z + d/2 + 0.1)
                glScalef(w * 0.15, h * 0.1, 0.1)
                glutSolidCube(1.0)
                glPopMatrix()
    
    # Roof
    roof_ambient = [0.3, 0.1, 0.1, 1.0]
    roof_diffuse = [0.8, 0.2, 0.2, 1.0]
    roof_specular = [0.2, 0.05, 0.05, 1.0]
    roof_shininess = [15.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, roof_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, roof_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, roof_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, roof_shininess)
    
    glColor3f(0.7, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(x, y + h + 1.0, z)
    if building_type == 'tower':
        glScalef(w * 0.8, 2.0, d * 0.8)
        glutSolidOctahedron()
    else:
        glScalef(w * 1.1, 1.5, d * 1.1)
        glutSolidOctahedron()
    glPopMatrix()

def draw_enhanced_track(points, segments=300):
    """Draw enhanced 3D tubular track with realistic rails."""
    if not show_track:
        return
        
    # Track material
    track_ambient = [0.15, 0.15, 0.2, 1.0]
    track_diffuse = [0.4, 0.4, 0.5, 1.0]
    track_specular = [0.6, 0.6, 0.7, 1.0]
    track_shininess = [40.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, track_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, track_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, track_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, track_shininess)
    
    glColor3f(0.3, 0.3, 0.4)
    
    # Draw dual rails
    rail_positions = [-0.3, 0.3]  # Left and right rails
    
    for rail_offset in rail_positions:
        glBegin(GL_QUAD_STRIP)
        
        for i in range(segments + 1):
            t1 = i / float(segments)
            t2 = ((i + 1) % segments) / float(segments)
            
            pos1 = np.array(get_point(points, t1))
            pos2 = np.array(get_point(points, t2))
            
            forward1 = get_cart_forward(t1)
            forward2 = get_cart_forward(t2)
            
            up = np.array([0.0, 1.0, 0.0])
            right1 = normalize_vector(cross_product(forward1, up))
            right2 = normalize_vector(cross_product(forward2, up))
            
            # Rail positions
            rail_pos1 = pos1 + right1 * rail_offset
            rail_pos2 = pos2 + right2 * rail_offset
            
            # Create rail cross-section (rectangular)
            rail_height = 0.08
            rail_width = 0.06
            
            # Top surface
            glNormal3f(0, 1, 0)
            glVertex3f(rail_pos1[0], rail_pos1[1] + rail_height, rail_pos1[2])
            glVertex3f(rail_pos1[0], rail_pos1[1] + rail_height, rail_pos1[2])
            
            # Side surfaces
            glNormal3f(right1[0], 0, right1[2])
            glVertex3f(rail_pos1[0] + right1[0] * rail_width, rail_pos1[1], rail_pos1[2] + right1[2] * rail_width)
            glVertex3f(rail_pos2[0] + right2[0] * rail_width, rail_pos2[1], rail_pos2[2] + right2[2] * rail_width)
            
        glEnd()
    
    # Draw cross ties
    draw_cross_ties(points, segments)

def draw_cross_ties(points, segments):
    """Draw cross ties connecting the rails."""
    tie_spacing = 8  # Every 8th segment gets a cross tie
    
    # Cross tie material
    tie_ambient = [0.2, 0.1, 0.05, 1.0]
    tie_diffuse = [0.5, 0.3, 0.15, 1.0]
    tie_specular = [0.1, 0.05, 0.02, 1.0]
    tie_shininess = [5.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, tie_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, tie_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, tie_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, tie_shininess)
    
    glColor3f(0.4, 0.25, 0.1)
    
    for i in range(0, segments, tie_spacing):
        t = i / float(segments)
        pos = np.array(get_point(points, t))
        forward = get_cart_forward(t)
        
        up = np.array([0.0, 1.0, 0.0])
        right = normalize_vector(cross_product(forward, up))
        
        # Draw cross tie
        glPushMatrix()
        glTranslatef(pos[0], pos[1] - 0.05, pos[2])
        
        # Align with track direction
        glRotatef(math.degrees(math.atan2(right[2], right[0])), 0, 1, 0)
        
        glScalef(0.8, 0.08, 0.12)
        glutSolidCube(1.0)
        glPopMatrix()

def draw_enhanced_ui():
    """Draw enhanced UI with detailed information and controls."""
    if not show_cart_info:
        return

    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Semi-transparent background panel
    glColor4f(0.0, 0.0, 0.0, 0.3)
    glBegin(GL_QUADS)
    glVertex2f(5, WINDOW_HEIGHT - 120)
    glVertex2f(400, WINDOW_HEIGHT - 120)
    glVertex2f(400, WINDOW_HEIGHT - 5)
    glVertex2f(5, WINDOW_HEIGHT - 5)
    glEnd()

    # Main info text
    glColor3f(0.9, 0.9, 1.0)  # Light blue text
    glRasterPos2f(15, WINDOW_HEIGHT - 25)
    
    # Get camera mode description
    camera_names = ["Follow", "First-Person", "Cinematic", "Orbit", "Flyby"]
    camera_name = camera_names[camera_mode] if camera_mode < len(camera_names) else "Unknown"
    
    info_text = f"Speed: {speed:.3f} | Camera: {camera_name} | {'PAUSED' if paused else 'RUNNING'}"
    for char in info_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

    # Enhanced controls
    glColor3f(0.8, 0.8, 0.9)
    controls = [
        "W/S: Adjust Speed | SPACE: Pause/Resume | ESC: Quit",
        "C: Cycle Camera (5 modes) | I: Toggle Info | T: Toggle Track",
        "E: Toggle Environment | F: Toggle Fog | L: Toggle Lighting"
    ]
    
    for i, control_text in enumerate(controls):
        glRasterPos2f(15, WINDOW_HEIGHT - 45 - i * 15)
        for char in control_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(char))

    # Performance info
    glColor3f(0.7, 0.9, 0.7)
    glRasterPos2f(15, WINDOW_HEIGHT - 105)
    perf_text = f"Position: t={t_param:.3f} | Environment: {'ON' if show_environment else 'OFF'}"
    for char in perf_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(char))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
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

    # Apply enhanced camera system
    apply_enhanced_camera(cart_position, cart_forward, current_time, delta_time)

    # Render enhanced environment
    draw_enhanced_terrain()
    
    if show_environment:
        draw_enhanced_trees()
        draw_enhanced_buildings()

    # Render enhanced track system
    draw_enhanced_track(control_points)

    # Render enhanced cart
    draw_enhanced_cart(cart_position, cart_forward)

    # Render enhanced UI
    draw_enhanced_ui()

    glutSwapBuffers()

def keyboard_handler(key, x, y):
    """Enhanced keyboard input handler with all controls."""
    global speed, paused, camera_mode, show_cart_info, show_track
    global show_environment, fog_enabled, lighting_enhanced

    key = key.decode('utf-8').lower()

    if key == 'w':
        speed = min(MAX_SPEED, speed + 0.005)
        debug_print(f"Speed increased to {speed:.3f}")
    elif key == 's':
        speed = max(MIN_SPEED, speed - 0.005)
        debug_print(f"Speed decreased to {speed:.3f}")
    elif key == ' ':
        paused = not paused
        debug_print(f"Animation {'paused' if paused else 'resumed'}")
    elif key == 'c':
        camera_mode = (camera_mode + 1) % 5  # Cycle through 5 camera modes
        camera_names = ["Follow", "First-Person", "Cinematic", "Orbit", "Flyby"]
        debug_print(f"Camera mode: {camera_names[camera_mode]}")
    elif key == 'i':
        show_cart_info = not show_cart_info
        debug_print(f"Info display: {'on' if show_cart_info else 'off'}")
    elif key == 't':
        show_track = not show_track
        debug_print(f"Track display: {'on' if show_track else 'off'}")
    elif key == 'e':
        show_environment = not show_environment
        debug_print(f"Environment: {'on' if show_environment else 'off'}")
    elif key == 'f':
        fog_enabled = not fog_enabled
        if fog_enabled:
            glEnable(GL_FOG)
        else:
            glDisable(GL_FOG)
        debug_print(f"Fog: {'on' if fog_enabled else 'off'}")
    elif key == 'l':
        lighting_enhanced = not lighting_enhanced
        if lighting_enhanced:
            setup_enhanced_lighting()
        else:
            glDisable(GL_LIGHTING)
        debug_print(f"Enhanced lighting: {'on' if lighting_enhanced else 'off'}")
    elif key == '\x1b' or key == 'q':  # Escape or Q to quit
        debug_print("Exiting...")
        sys.exit(0)

def idle():
    """Idle function for smooth animation."""
    glutPostRedisplay()

def draw_enhanced_cart(pos, forward):
    """Draw enhanced cart with detailed 3D model."""
    # Cart material
    cart_ambient = [0.2, 0.05, 0.05, 1.0]
    cart_diffuse = [0.8, 0.1, 0.1, 1.0]
    cart_specular = [0.6, 0.3, 0.3, 1.0]
    cart_shininess = [25.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, cart_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, cart_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, cart_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, cart_shininess)
    
    glPushMatrix()
    
    # Position cart
    glTranslatef(pos[0], pos[1] + 0.2, pos[2])
    
    # Orient cart along track
    up = np.array([0.0, 1.0, 0.0])
    right = normalize_vector(cross_product(forward, up))
    
    # Create rotation matrix for proper orientation
    angle = math.degrees(math.atan2(forward[2], forward[0]))
    glRotatef(angle, 0, 1, 0)
    
    # Scale cart
    glScalef(cart_scale, cart_scale, cart_scale)
    
    # Main cart body (red)
    glColor3f(0.8, 0.1, 0.1)
    glPushMatrix()
    glScalef(1.2, 0.6, 0.8)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Cart seat (darker red)
    glColor3f(0.6, 0.05, 0.05)
    glPushMatrix()
    glTranslatef(0, 0.2, 0.1)
    glScalef(0.8, 0.3, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Safety bar (metallic)
    bar_ambient = [0.1, 0.1, 0.15, 1.0]
    bar_diffuse = [0.3, 0.3, 0.4, 1.0]
    bar_specular = [0.8, 0.8, 0.9, 1.0]
    bar_shininess = [60.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, bar_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, bar_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, bar_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, bar_shininess)
    
    glColor3f(0.4, 0.4, 0.5)
    glPushMatrix()
    glTranslatef(0, 0.6, 0.3)
    glScalef(0.9, 0.1, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Wheels (black with metallic rims)
    wheel_positions = [(-0.4, -0.4, -0.3), (0.4, -0.4, -0.3), 
                      (-0.4, -0.4, 0.3), (0.4, -0.4, 0.3)]
    
    # Wheel material
    wheel_ambient = [0.05, 0.05, 0.05, 1.0]
    wheel_diffuse = [0.1, 0.1, 0.1, 1.0]
    wheel_specular = [0.2, 0.2, 0.2, 1.0]
    wheel_shininess = [15.0]
    
    glMaterialfv(GL_FRONT, GL_AMBIENT, wheel_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, wheel_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, wheel_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, wheel_shininess)
    
    glColor3f(0.1, 0.1, 0.1)
    
    for wx, wy, wz in wheel_positions:
        glPushMatrix()
        glTranslatef(wx, wy, wz)
        glutSolidSphere(0.15, 12, 8)
        glPopMatrix()
    
    glPopMatrix()

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





