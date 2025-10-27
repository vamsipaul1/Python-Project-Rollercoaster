@echo off
echo Installing freeglut for Roller Coaster Simulation...
echo.

REM Download freeglut (this is a placeholder - user needs to download manually)
echo Step 1: Please download freeglut from:
echo http://freeglut.sourceforge.net/
echo.

REM Alternative: Try to find existing installation
echo Step 2: Looking for existing freeglut installation...
if exist "C:\Windows\System32\freeglut.dll" (
    echo ✓ freeglut.dll already exists in System32
    goto :verify
)

if exist "C:\Windows\SysWOW64\freeglut.dll" (
    echo ✓ freeglut.dll found in SysWOW64
    goto :verify
)

echo Step 3: Please copy freeglut.dll to C:\Windows\System32\
echo (Download from: http://freeglut.sourceforge.net/)
echo.

:verify
echo Step 4: Testing installation...
python -c "
try:
    from OpenGL.GLUT import glutInit
    import sys
    sys.argv = ['test']
    glutInit()
    print('SUCCESS: freeglut is working!')
except Exception as e:
    print('ERROR:', str(e))
    print('Please ensure freeglut.dll is in C:\Windows\System32\')
"

echo.
echo Step 5: Run the simulation
echo python main.py
echo.
pause
