# Quickstart Guide: Digital Twin Module (Gazebo & Unity)

**Feature**: Digital Twin Module (Gazebo & Unity)
**Created**: 2025-12-10
**Status**: Completed

## Prerequisites

Before starting with the Digital Twin module, ensure you have:

- **Gazebo Classic or Garden** installed (tested with version 11.x or 4.x+)
- **Unity Hub** with Unity 2021.3 LTS or newer
- **Basic understanding** of robotics concepts (kinematics, sensors)
- **Markdown editor** for content creation and review
- **Git** for version control (if using the full repository)

### System Requirements
- Operating System: Ubuntu 20.04+ or Windows 10+
- RAM: 8GB minimum (16GB recommended)
- Storage: 10GB available space
- Graphics: OpenGL 3.3+ compatible GPU

## Getting Started

### 1. Environment Setup

First, verify your Gazebo installation:

```bash
gz version  # For Gazebo Garden
# OR
gazebo --version  # For Gazebo Classic
```

Verify your Unity installation:

```bash
# Check Unity Hub is installed and accessible
unity-hub --version
```

### 2. Repository Structure

Navigate to the digital twin module:

```bash
cd docs/modules/digital-twin/
```

The module contains:
- `chapters/` - Educational content for each topic
- `examples/` - Sample configurations and projects
- `diagrams/` - Visual aids for understanding concepts

### 3. Chapter 1: Gazebo Physics Fundamentals

Start with the physics simulation concepts:

```bash
# Review the example configurations
ls examples/gazebo/
# Run a basic physics simulation
cd examples/gazebo/basic-physics
# Launch the simulation (instructions in README.md)
```

### 4. Chapter 2: Unity Environment Design

Explore the visualization environment:

```bash
# Review Unity project examples
ls examples/unity/
# Open the sample project in Unity Hub
# Import the project located in examples/unity/basic-environment
```

### 5. Chapter 3: Sensor Simulation Pipeline

Implement sensor simulation:

```bash
# Review sensor configuration examples
ls examples/sensors/
# Test different sensor types
cd examples/sensors/lidar
# Run sensor simulation (instructions in README.md)
```

## Basic Example: Simple Humanoid Scene

Follow this step-by-step tutorial to create your first integrated simulation:

### Step 1: Create a Basic Robot Model

Create a simple humanoid robot in SDF format:

```xml
<sdf version='1.7'>
  <model name='simple_humanoid'>
    <link name='torso'>
      <pose>0 0 0.5 0 0 0</pose>
      <collision name='collision'>
        <geometry>
          <box><size>0.5 0.3 1.0</size></box>
        </geometry>
      </collision>
      <visual name='visual'>
        <geometry>
          <box><size>0.5 0.3 1.0</size></box>
        </geometry>
      </visual>
    </link>
  </model>
</sdf>
```

### Step 2: Set Up Physics Environment

Create a basic environment with ground plane:

```xml
<sdf version='1.7'>
  <world name='humanoid_world'>
    <include>
      <uri>model://ground_plane</uri>
    </include>
    <include>
      <uri>model://sun</uri>
    </include>
  </world>
</sdf>
```

### Step 3: Test Physics Simulation

Run the simulation to verify physics behavior:

```bash
# From the examples directory
gz sim -r simple_humanoid.sdf  # For Gazebo Garden
# OR
gazebo simple_humanoid.world  # For Gazebo Classic
```

### Step 4: Unity Visualization

Import the same model into Unity for visualization:

1. Open Unity Hub and create a new 3D project
2. Import the robot model (converted to .fbx or .obj format)
3. Create a similar scene layout as in Gazebo
4. Set up lighting to match the simulation environment

## Troubleshooting

### Common Issues

**Gazebo won't start:**
- Check if NVIDIA drivers are properly installed (for GPU acceleration)
- Verify gazebo packages are installed: `apt list --installed | grep gazebo`
- Try running with software rendering: `export LIBGL_ALWAYS_SOFTWARE=1`

**Unity performance issues:**
- Reduce rendering quality in Unity settings
- Close other applications to free up RAM
- Check that your GPU meets minimum requirements

**Sensor data not generating:**
- Verify sensor plugins are properly loaded
- Check that the simulation is running at sufficient update rate
- Ensure sensor configurations match expected formats

### Getting Help

- Review the Gazebo documentation: http://gazebosim.org/tutorials
- Check Unity robotics documentation: https://unity.com/solutions/industrial-automation
- Consult the ROS/ROS2 robotics community for integration issues

## Next Steps

After completing this quickstart:

1. Explore more complex robot models in the examples directory
2. Experiment with different sensor configurations
3. Try integrating Gazebo physics with Unity visualization
4. Work through the full tutorial sequence in order
5. Create your own custom humanoid robot simulation