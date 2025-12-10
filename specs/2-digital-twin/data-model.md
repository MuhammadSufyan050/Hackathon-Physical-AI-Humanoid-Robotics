# Data Model: Digital Twin Module (Gazebo & Unity)

**Feature**: Digital Twin Module (Gazebo & Unity)
**Created**: 2025-12-10
**Status**: Completed

## Entity: Physics Simulation

**Description**: Represents the mathematical models that govern object behavior, including gravity, collisions, and forces in the simulation environment.

**Fields**:
- `gravity_vector`: 3D vector representing gravitational force (x, y, z components)
- `collision_meshes`: Collection of geometric shapes used for collision detection
- `joint_constraints`: Parameters defining joint movement limits and behavior
- `material_properties`: Physical properties affecting object interactions (friction, restitution)
- `simulation_step_size`: Time increment for physics calculations
- `update_rate`: Frequency of physics calculations per second

**Relationships**:
- Belongs to: Environment
- Connected to: Robot Model (one-to-many)

**Validation Rules**:
- Gravity vector must have realistic values (typically -9.81 m/s² in z direction)
- Collision meshes must be valid geometric shapes
- Joint constraints must be within physically possible ranges
- Update rate must be within performance constraints

## Entity: Robot Model

**Description**: Represents the digital representation of a physical robot, including geometry, joints, and sensors.

**Fields**:
- `model_name`: Unique identifier for the robot model
- `geometry`: Visual and collision geometry definitions
- `joints`: Collection of joint configurations (revolute, prismatic, fixed)
- `sensors`: Collection of sensor configurations attached to the robot
- `physical_properties`: Mass, center of mass, and inertia tensor
- `links`: Collection of rigid body components
- `actuators`: Motor specifications and control parameters

**Relationships**:
- Contains: Physics Simulation (one-to-one)
- Connected to: Sensor Data (one-to-many)
- Belongs to: Environment (one-to-many)

**Validation Rules**:
- Model must be valid URDF/SDF format
- All joints must have defined limits and properties
- Mass and inertia values must be physically realistic
- Sensor configurations must be compatible with simulation engine

## Entity: Sensor Data

**Description**: Represents the information captured by simulated sensors (LiDAR, depth cameras, IMUs).

**Fields**:
- `sensor_type`: Type of sensor (LiDAR, depth_camera, IMU)
- `data_format`: Format of the sensor output (point_cloud, depth_map, acceleration_orientation)
- `sampling_rate`: Frequency of data collection
- `accuracy_metrics`: Error bounds and noise characteristics
- `timestamp`: Time of data collection
- `frame_of_reference`: Coordinate system for the data
- `field_of_view`: Angular coverage for the sensor (where applicable)

**Relationships**:
- Generated from: Robot Model (many-to-one)
- Belongs to: Environment (many-to-one)

**Validation Rules**:
- Data format must match sensor type specifications
- Sampling rate must be within realistic bounds
- Accuracy metrics must reflect realistic sensor characteristics
- Timestamps must be consistent with simulation time

## Entity: Environment

**Description**: Represents the 3D space where simulation occurs, including terrain, obstacles, and lighting conditions.

**Fields**:
- `environment_name`: Unique identifier for the environment
- `terrain_data`: Height map and surface properties
- `lighting_config`: Light sources, intensities, and positions
- `object_positions`: Positions and properties of static objects
- `material_properties`: Surface properties affecting physics interactions
- `simulation_bounds`: Physical limits of the simulation space

**Relationships**:
- Contains: Physics Simulation (one-to-many)
- Contains: Robot Model (one-to-many)
- Contains: Sensor Data (one-to-many)

**Validation Rules**:
- Terrain data must be valid and within simulation bounds
- Lighting configuration must be physically plausible
- Object positions must not create impossible physics states
- Environment bounds must be reasonable for the simulation

## State Transitions

### Physics Simulation States
- `initializing` → `running`: When simulation begins
- `running` → `paused`: When simulation is temporarily stopped
- `paused` → `running`: When simulation resumes
- `running` → `error`: When physics calculations fail
- `running` → `completed`: When simulation ends

### Robot Model States
- `loaded` → `positioned`: When robot is placed in environment
- `positioned` → `simulating`: When physics simulation begins
- `simulating` → `interacting`: When robot interacts with environment
- `interacting` → `idle`: When robot stops moving
- `interacting` → `error`: When robot behavior is invalid

## Data Flow Patterns

### Physics Update Cycle
1. Environment state is read
2. Robot model properties are applied
3. Physics calculations are performed
4. New positions and velocities are computed
5. Collision detection is performed
6. Sensor data is generated
7. State is updated for visualization

### Sensor Data Generation
1. Environment state is sampled
2. Sensor configuration is applied
3. Physics interactions are calculated
4. Raw sensor data is generated
5. Noise and accuracy factors are applied
6. Processed data is formatted
7. Data is timestamped and stored