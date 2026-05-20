# Robot Arm Maze Solver

End-to-end system that photographs a physical maze, solves it with A*, and commands a 6-DOF robot arm to trace the solution path in the real world. The pipeline runs across Python (vision + pathfinding), MATLAB (inverse kinematics + trajectory generation), and a TCP socket interface to the Pro600 hardware.

---

## Hardware Demo

<p align="center">
  <img src="media/demo.gif" width="480" alt="Robot arm tracing solved maze path on hardware"/>
</p>

Full video: https://github.com/Hp092/robot-arm-maze-solver/blob/main/DemoVideo.mp4

---

## MATLAB Simulation

<p align="center">
  <img src="media/simulation.gif" width="560" alt="MATLAB 3D robot arm simulation following maze trajectory"/>
</p>

Full video: https://github.com/Hp092/robot-arm-maze-solver/blob/main/SimulationVideo.mp4

---

## A* Maze Solution

The A* solver generates an optimal path through the maze. Waypoint coordinates are exported to CSV and fed into the IK solver.

<p align="center">
  <img src="media/maze_solved.png" width="720" alt="A* solved maze paths — 4x4 and 50x50"/>
</p>

---

## Pipeline Overview

```
Camera → A* Pathfinding → Waypoints CSV → Pixel→World Mapping → IK Solver → Joint Angles CSV → Robot Hardware
 (maze.py)                                    (mapper.m)          (FinalProject.m)              (robotControl.py)
```

1. **maze.py** — captures the maze from a webcam, binarizes it, runs A* with a distance-transform cost map to prefer paths away from walls, simplifies the route with Ramer–Douglas–Peucker, and saves pixel waypoints to `waypoints.csv`
2. **mapper.m** — converts pixel coordinates from the image to real-world robot workspace coordinates (metres) using calibrated reference points *(see below)*
3. **FinalProject.m** — loads the Pro600 URDF, calls `mapper.m` on each waypoint, solves inverse kinematics, generates a smooth trapezoidal velocity trajectory, simulates the arm, and exports joint angles to `ik_joint_angles.csv`
4. **robotControl.py** — reads the joint angle CSV and sends `set_angles(...)` commands over TCP to the physical robot at each waypoint

---

## Pixel-to-World Mapping — `mapper.m`

The camera sees the maze in pixel coordinates, but the robot arm works in metres in 3D space. `mapper.m` bridges this gap using a **calibrated linear mapping**.

**How it works:**

Eight physical reference points on the workspace were manually measured — each one has a known pixel location `(px, py)` and a known real-world position `(x_m, y_m)` in metres. These are stored as pairs in the file:

```matlab
refx1 = [203, -0.3299];  % pixel x=203 maps to world x=-0.3299 m
refy1 = [96,  -0.2007];  % pixel y=96  maps to world y=-0.2007 m
```

From each pair of reference points, `line_gen.m` fits a line (`y = mx + c`) that describes the pixel→world relationship. Four such lines are averaged together for both x and y independently, making the mapping robust against noise in any single measurement:

```matlab
mx = (mx1 + mx2 + mx3 + mx4) / 4;
x_m = mx * x_px + cx;   % linear map: pixels → metres
y_m = my * y_px + cy;
```

The z coordinate is fixed at `0.0692 m` — the height of the maze surface above the robot's base.

**Why this matters:** Without this mapping, the IK solver would receive pixel numbers as if they were metre coordinates, placing the robot arm wildly out of position. `mapper.m` is what ties the vision system to the physical robot frame.

---

## Hardware

| Component | Details |
|---|---|
| Robot arm | Efort Pro600 — 6-DOF industrial arm |
| End effector | Link 6 (wrist) |
| Camera | Webcam (OpenCV capture) |
| Communication | TCP socket to robot controller |

---

## Software

| Layer | Technology |
|---|---|
| Maze solving | Python, OpenCV, A* with distance-transform cost |
| Path simplification | Ramer–Douglas–Peucker algorithm |
| Pixel→world calibration | Linear regression on 8 reference points (`mapper.m`) |
| Robot modeling | MATLAB Robotics Toolbox, URDF |
| Inverse kinematics | MATLAB `inverseKinematics` solver |
| Trajectory generation | Trapezoidal velocity profile (`trapveltraj`) |
| Hardware interface | Python TCP socket |

---

## Repository Structure

```
robot-arm-maze-solver/
├── FinalProject.m            # Main MATLAB script — IK, trajectory, simulation
├── mapper.m                  # Pixel-to-world coordinate mapping
├── line_gen.m                # Linear fit helper used by mapper.m
├── csvimport.m               # CSV import helper
├── TrajPlanning_Orientation.m  # Trajectory planning with orientation
├── createWaypointData.m      # Waypoint data helper
├── Lab_4.mlx                 # MATLAB live script (annotated walkthrough)
├── maze.py / maze_solver.py  # Maze capture and A* solver
├── robotControl.py           # TCP interface to physical robot hardware
├── server.py / home.py       # Robot server and home-position scripts
├── python/                   # Additional camera and server scripts
├── waypoints.csv             # Example solved maze waypoints (pixel coords)
├── JointAngles.csv           # Example output joint angles
├── ik_joint_angles.csv       # IK-computed joint angles for hardware
├── FinalProject.pdf          # Project report
├── DemoVideo.mp4             # Hardware demo
├── SimulationVideo.mp4       # MATLAB simulation demo
└── URDF/
    ├── pro600.urdf           # Robot description
    ├── base.dae              # Base mesh
    ├── link1–6.dae           # Link meshes
    └── iksessiondata.mat     # IK session data
```

---

## Getting Started

**Requirements:** MATLAB R2023b+, Robotics System Toolbox; Python 3 with `opencv-python`, `numpy`

### Step 1 — Solve the maze

```bash
python maze_solver.py
```

Press `s` to capture the maze from the webcam. Click the start and end points. The solved path is saved to `waypoints.csv`.

### Step 2 — Run the MATLAB simulation

Open MATLAB, set the Current Folder to the project root, and run:

```matlab
run('FinalProject.m')
```

This loads the URDF, maps pixel waypoints to world coordinates via `mapper.m`, runs IK, animates the 3D simulation, and saves `ik_joint_angles.csv`.

### Step 3 — Run on hardware

Update `TARGET_IP` in `robotControl.py` to match your robot controller, then:

```bash
python robotControl.py
```

---

## Author

**Harsh Padmalwar**
