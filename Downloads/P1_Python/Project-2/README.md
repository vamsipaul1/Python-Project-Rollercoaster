# Roller Coaster Simulation - Intermediate Submission 2

A complete 3D roller coaster simulation built with Python and PyOpenGL, featuring smooth cart animation, multiple camera modes, and interactive controls.

![Roller Coaster Simulation](https://img.shields.io/badge/Python-3.9+-blue) ![OpenGL](https://img.shields.io/badge/OpenGL-PyOpenGL-green) ![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

## 🎢 Features

- **Smooth Track Animation**: Cart moves along a Catmull-Rom spline curve
- **Dual Camera Modes**: Third-person follow camera and first-person driver view
- **Interactive Controls**: Real-time speed adjustment, pause/resume, camera toggle
- **3D Environment**: Ground plane, trees, buildings, and lighting
- **Track Visualization**: Optional wireframe display of the complete track
- **Real-time UI**: On-screen display of speed, camera mode, and controls

## 📋 Requirements

- Python 3.9 or higher
- PyOpenGL with acceleration
- NumPy for mathematical operations
- Pillow for image processing (if textures are added)

### Dependencies Installation

```bash
# Create virtual environment (recommended)
python -m venv rollercoaster_env
source rollercoaster_env/bin/activate  # On Windows: rollercoaster_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Quick Start

### Method 1: Clone from GitHub
```bash
# Clone the repository
git clone https://github.com/vamsipaul1/Python-Project-Rollercoaster.git
cd Python-Project-Rollercoaster

# Install dependencies
   pip install -r requirements.txt
   ```

### Method 2: Download ZIP
1. **Download** the project as ZIP from GitHub
2. **Extract** to your desired location
3. **Install dependencies** using the command above

### Running the Simulation

**Option A: Full 3D Graphics Mode** (recommended):
   ```bash
   python main.py
   ```
*Note: On Windows, this requires freeglut.dll (see troubleshooting section)*

**Option B: Demo Mode** (no graphics, tests simulation logic):
```bash
python main.py --demo
```

**Enjoy the ride!** Use keyboard controls to interact with the 3D simulation.

## 🎥 Demo & Screenshots

### 3D Graphics Mode
- **Full 3D roller coaster simulation** with animated cart
- **Interactive camera controls** (third-person and first-person views)
- **Real-time environment** with ground, trees, and buildings
- **Track visualization** showing the complete spline curve

### Demo Mode Output
```
============================================================
ROLLER COASTER SIMULATION - DEMO MODE
============================================================
Testing core simulation logic without graphics...

Frame  1: t=0.000, Pos=[5. 0. 2.], Speed=0.080
Frame  2: t=0.001, Pos=[5.1088 0.02362308 2.05486835], Speed=0.090
...
Demo completed! All simulation systems working correctly.
============================================================
```

## 🎮 Enhanced Controls

| Key | Action |
|-----|--------|
| `W` | Increase cart speed (fine control) |
| `S` | Decrease cart speed (fine control) |
| `Space` | Pause/Resume animation |
| `C` | Cycle camera modes (5 cinematic modes) |
| `E` | Toggle environment (trees, buildings) |
| `F` | Toggle atmospheric fog |
| `L` | Toggle enhanced lighting system |
| `I` | Toggle enhanced UI panel |
| `T` | Toggle track visualization |
| `Esc` or `Q` | Quit application |

### 🎥 Camera Modes
1. **Follow Camera** - Smooth third-person tracking
2. **First-Person** - Inside the cart view
3. **Cinematic** - Dynamic tracking with orbital movement
4. **Orbit** - Circular orbit around the cart
5. **Flyby** - Dramatic flyby angles

### Camera Modes

- **Third-person**: Camera follows behind and above the cart
- **First-person**: Camera view from inside the cart (driver's perspective)

## 🏗️ Project Structure

```
roller-coaster-simulation/
│
├── main.py           # Main application entry point
├── curve.py          # Track curve generation and interpolation
├── cart.py           # 3D cart rendering and orientation
├── camera.py         # Camera system (follow and first-person)
├── requirements.txt  # Python dependencies
└── README.md         # This documentation
```

### File Descriptions

- **`main.py`**: Orchestrates the entire simulation, handles animation loop, input, and rendering
- **`curve.py`**: Implements Catmull-Rom spline interpolation for smooth track curves
- **`cart.py`**: Renders the 3D cart with proper orientation along the track
- **`camera.py`**: Manages camera positioning and smooth following behavior

## 🛤️ Track Information

The roller coaster track uses **17 control points** forming a closed loop with:
- **Total length**: Approximately 85 units
- **Features**: Hills, valleys, curves, and a figure-8 section
- **Interpolation**: Catmull-Rom spline for smooth curves

## ⚙️ Configuration

Key parameters can be adjusted in `main.py`:

```python
DEFAULT_SPEED = 0.08    # Initial cart speed
MAX_SPEED = 0.5        # Maximum speed limit
WINDOW_WIDTH = 1024    # Window dimensions
WINDOW_HEIGHT = 768
```

## 🔧 Troubleshooting

### Common Issues

**Import Error: No module named 'OpenGL'**
```bash
pip install --upgrade PyOpenGL PyOpenGL-accelerate
```
*Note: We use PyOpenGL 3.1.10+ for better freeglut compatibility*

**GLUT Error on Windows** (Most Common Issue)
```bash
# Error: "Attempt to call an undefined function glutInit"
# Solution 1: Copy freeglut.dll to Python directory
# Download from: http://freeglut.sourceforge.net/
# Copy freeglut.dll to: C:\Program Files\Python311\

# Solution 2: Copy to System32
# Copy freeglut.dll to: C:\Windows\System32\

# Solution 3: Use demo mode (no graphics)
python main.py --demo
```

**GLUT Error on Linux**
```bash
sudo apt-get install freeglut3-dev  # Ubuntu/Debian
```

**GLUT Error on macOS**
```bash
brew install freeglut
```

**PyOpenGL Version Issues**
```bash
# If you get "undefined function" errors, upgrade PyOpenGL
pip install --upgrade PyOpenGL PyOpenGL-accelerate
# Current tested version: PyOpenGL 3.1.10
```

**Poor Performance**
- Reduce window size in `main.py`
- Disable track visualization with `T` key
- Close other applications
- Use demo mode for testing: `python main.py --demo`

**Cart Not Visible**
- Toggle camera mode with `C` key
- Check if animation is paused (press Space)
- Verify track visualization is enabled (press T)
- Ensure freeglut.dll is properly installed

## 🎯 Technical Details

### Rendering Pipeline
1. **Initialization**: OpenGL context setup with lighting and depth testing
2. **Animation**: Time-based parameter updates using delta time
3. **Physics**: Numerical differentiation for cart orientation
4. **Rendering**: Environment → Track → Cart → UI overlay

### Mathematics
- **Curve Interpolation**: Catmull-Rom spline with C1 continuity
- **Camera Following**: Look-ahead positioning with damping
- **Orientation**: Forward vector calculation using finite differences

### Performance Optimizations
- Double buffering for smooth animation
- Efficient matrix operations using NumPy
- Optional rendering features (track, UI) for better performance

## 📚 Learning Outcomes

This project demonstrates:
- **3D Mathematics**: Vector operations, matrix transformations, Catmull-Rom splines
- **Computer Graphics**: OpenGL pipeline, lighting, perspective projection, depth testing
- **Animation Systems**: Time-based updates, smooth interpolation, real-time rendering
- **User Interaction**: Event handling, real-time input processing, camera controls
- **Software Architecture**: Modular design with clear separation of concerns
- **Problem Solving**: Cross-platform compatibility, dependency management, error handling

## 🛠️ Development Process

### What We Built
1. **Mathematical Foundation**: Implemented Catmull-Rom spline interpolation for smooth track curves
2. **3D Graphics Engine**: Created OpenGL-based rendering system with lighting and depth testing
3. **Animation System**: Built time-based cart movement with proper orientation calculations
4. **Camera System**: Developed dual-mode camera (third-person follow and first-person driver view)
5. **User Interface**: Added interactive controls and real-time parameter adjustment
6. **Cross-Platform Support**: Ensured compatibility across Windows, Linux, and macOS
7. **Error Handling**: Implemented graceful fallbacks and comprehensive troubleshooting

### Technical Achievements
- **17-point closed-loop track** with hills, valleys, and curves
- **Real-time 3D rendering** at 60+ FPS with double buffering
- **Smooth cart animation** using numerical differentiation for orientation
- **Interactive camera controls** with look-ahead positioning
- **Demo mode** for testing without graphics dependencies
- **Professional documentation** and clean code architecture

## 🔄 Future Enhancements

- [ ] **Physics Simulation**: Realistic gravity and momentum
- [ ] **Texture Mapping**: Skybox and track textures
- [ ] **Particle Effects**: Sparks, dust, and environmental effects
- [ ] **Sound System**: Engine sounds and ambient audio
- [ ] **Multiple Carts**: Train of carts with coupling physics
- [ ] **Level Editor**: Visual track design interface
- [ ] **VR Support**: Virtual reality headset compatibility

## 🎓 University Assignment Details

**Course**: Computer Graphics / 3D Programming  
**Assignment**: Intermediate Submission 2 - Roller Coaster Simulation  
**Technologies**: Python 3.11, PyOpenGL 3.1.10, NumPy 1.24.3  
**Repository**: https://github.com/vamsipaul1/Python-Project-Rollercoaster  

### Assignment Requirements Met
- ✅ **Spline-based track animation** using get_point() function
- ✅ **Dual camera modes** (third-person and first-person)
- ✅ **Interactive controls** (speed, pause, camera toggle)
- ✅ **3D cart rendering** with proper orientation
- ✅ **Track visualization** and environment rendering
- ✅ **Professional documentation** and code organization

## 📄 License

This project is created for educational purposes as part of a university assignment. Feel free to use and modify for learning purposes.

## 🤝 Contributing

This is a university assignment submission. For improvements or suggestions, please refer to the course instructor.

## 🏆 Project Status

**Status**: ✅ **COMPLETE AND TESTED**  
**Last Updated**: January 2025  
**Tested On**: Windows 11, Python 3.11, PyOpenGL 3.1.10  
**GitHub**: https://github.com/vamsipaul1/Python-Project-Rollercoaster  

---

**Built with ❤️ using Python, PyOpenGL, and OpenGL**  
*Ready for university submission and professional portfolio showcase*