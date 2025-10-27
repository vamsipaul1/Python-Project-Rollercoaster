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

1. **Clone or download** this project
2. **Install dependencies** using the command above
3. **Run the simulation**:

   **Option A: With Graphics** (requires freeglut on Windows):
   ```bash
   python main.py
   ```

   **Option B: Demo Mode** (no graphics, tests simulation logic):
   ```bash
   python main.py --demo
   ```

4. **Enjoy the ride!** Use keyboard controls to interact

## 🎮 Controls

| Key | Action |
|-----|--------|
| `W` | Increase cart speed |
| `S` | Decrease cart speed |
| `Space` | Pause/Resume animation |
| `C` | Toggle camera mode (3rd person ↔ 1st person) |
| `I` | Toggle info display |
| `T` | Toggle track visualization |
| `Esc` or `Q` | Quit application |

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
pip install PyOpenGL PyOpenGL-accelerate
```

**GLUT Error on Linux**
```bash
sudo apt-get install freeglut3-dev  # Ubuntu/Debian
```

**GLUT Error on macOS**
```bash
brew install freeglut
```

**GLUT Error on Windows**
- Install [freeglut](http://freeglut.sourceforge.net/)
- Ensure `freeglut.dll` is in your system PATH

**Poor Performance**
- Reduce window size in `main.py`
- Disable track visualization with `T` key
- Close other applications

**Cart Not Visible**
- Toggle camera mode with `C` key
- Check if animation is paused (press Space)
- Verify track visualization is enabled (press T)

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
- **3D Mathematics**: Vector operations, matrix transformations
- **Computer Graphics**: OpenGL pipeline, lighting, perspective projection
- **Animation Systems**: Time-based updates, smooth interpolation
- **User Interaction**: Event handling, real-time input processing
- **Software Architecture**: Modular design with clear separation of concerns

## 🔄 Future Enhancements

- [ ] **Physics Simulation**: Realistic gravity and momentum
- [ ] **Texture Mapping**: Skybox and track textures
- [ ] **Particle Effects**: Sparks, dust, and environmental effects
- [ ] **Sound System**: Engine sounds and ambient audio
- [ ] **Multiple Carts**: Train of carts with coupling physics
- [ ] **Level Editor**: Visual track design interface
- [ ] **VR Support**: Virtual reality headset compatibility

## 📄 License

This project is created for educational purposes as part of a university assignment. Feel free to use and modify for learning purposes.

## 🤝 Contributing

This is a university assignment submission. For improvements or suggestions, please refer to the course instructor.

---

**Built with ❤️ using Python, PyOpenGL, and OpenGL**