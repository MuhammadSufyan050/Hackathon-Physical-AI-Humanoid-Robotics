# Quickstart Guide: Module 1 — The Robotic Nervous System (ROS 2)

## Overview
This quickstart guide will help you get up and running with the ROS 2 fundamentals covered in Module 1. You'll learn how to set up your environment, create your first ROS 2 nodes, and understand the basic communication patterns.

## Prerequisites
- Ubuntu 22.04 (recommended) or Windows 10/11 with WSL2
- Python 3.8 or higher
- Basic Python programming knowledge
- Familiarity with command line interfaces

## Setting Up ROS 2 Environment

### 1. Install ROS 2 Humble Hawksbill
Choose your platform:

**On Ubuntu:**
```bash
# Add the ROS 2 apt repository
sudo apt update && sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update
sudo apt install -y ros-humble-desktop
sudo apt install -y python3-rosdep2
sudo rosdep init
rosdep update
```

**On Windows with WSL2:**
```bash
# Install WSL2 with Ubuntu 22.04
wsl --install -d Ubuntu-22.04

# Then follow the Ubuntu instructions above
```

### 2. Source ROS 2 Environment
```bash
source /opt/ros/humble/setup.bash
```

To make this permanent, add it to your `.bashrc`:
```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

### 3. Create a ROS 2 Workspace
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
colcon build
source install/setup.bash
```

## Your First ROS 2 Node

### 1. Create a Package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python my_robot_agent --dependencies rclpy std_msgs
```

### 2. Create a Simple Publisher Node
Edit `~/ros2_ws/src/my_robot_agent/my_robot_agent/simple_publisher.py`:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimplePublisher(Node):
    def __init__(self):
        super().__init__('simple_publisher')
        self.publisher = self.create_publisher(String, 'robot_commands', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello Robot! Message #{self.i}'
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1


def main(args=None):
    rclpy.init(args=args)
    simple_publisher = SimplePublisher()
    rclpy.spin(simple_publisher)
    simple_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 3. Create a Simple Subscriber Node
Edit `~/ros2_ws/src/my_robot_agent/my_robot_agent/simple_subscriber.py`:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleSubscriber(Node):
    def __init__(self):
        super().__init__('simple_subscriber')
        self.subscription = self.create_subscription(
            String,
            'robot_commands',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    simple_subscriber = SimpleSubscriber()
    rclpy.spin(simple_subscriber)
    simple_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 4. Update setup.py
Edit `~/ros2_ws/src/my_robot_agent/setup.py` to include the new scripts:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'my_robot_agent'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Simple ROS 2 publisher and subscriber example',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_publisher = my_robot_agent.simple_publisher:main',
            'simple_subscriber = my_robot_agent.simple_subscriber:main',
        ],
    },
)
```

## Running Your Nodes

### 1. Build Your Package
```bash
cd ~/ros2_ws
colcon build --packages-select my_robot_agent
source install/setup.bash
```

### 2. Run the Publisher
```bash
ros2 run my_robot_agent simple_publisher
```

### 3. In a new terminal, run the Subscriber
```bash
cd ~/ros2_ws
source install/setup.bash
ros2 run my_robot_agent simple_subscriber
```

You should see the publisher sending messages and the subscriber receiving them!

## Exploring ROS 2 Tools

### 1. View the ROS 2 Graph
In a new terminal:
```bash
rqt_graph
```

### 2. List Topics
```bash
ros2 topic list
```

### 3. Echo Messages on a Topic
```bash
ros2 topic echo /robot_commands std_msgs/msg/String
```

### 4. Check Topic Information
```bash
ros2 topic info /robot_commands
```

## Python Agent Integration Example

Now let's create a simple Python agent that makes decisions based on sensor data:

Create `~/ros2_ws/src/my_robot_agent/my_robot_agent/decision_agent.py`:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int8
import random


class DecisionAgent(Node):
    def __init__(self):
        super().__init__('decision_agent')

        # Subscribe to sensor data
        self.sensor_subscription = self.create_subscription(
            String,
            'sensor_data',
            self.sensor_callback,
            10)

        # Publish commands to robot
        self.command_publisher = self.create_publisher(String, 'robot_commands', 10)

        # Timer for periodic decision making
        self.timer = self.create_timer(1.0, self.make_decision)

        self.last_sensor_data = "No data yet"
        self.decision_count = 0

    def sensor_callback(self, msg):
        self.last_sensor_data = msg.data
        self.get_logger().info(f'Agent received sensor data: "{msg.data}"')

    def make_decision(self):
        # Simple decision logic based on sensor data
        if "obstacle" in self.last_sensor_data.lower():
            command = "STOP"
        elif "clear" in self.last_sensor_data.lower():
            command = "MOVE_FORWARD"
        else:
            # Random decision if sensor data is ambiguous
            command = random.choice(["TURN_LEFT", "TURN_RIGHT", "MOVE_FORWARD"])

        # Publish the decision
        cmd_msg = String()
        cmd_msg.data = f"{command} #{self.decision_count}"
        self.command_publisher.publish(cmd_msg)
        self.get_logger().info(f'Agent decided: "{cmd_msg.data}"')

        self.decision_count += 1


def main(args=None):
    rclpy.init(args=args)
    agent = DecisionAgent()
    rclpy.spin(agent)
    agent.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

Update the setup.py console scripts section to include the agent:
```python
entry_points={
    'console_scripts': [
        'simple_publisher = my_robot_agent.simple_publisher:main',
        'simple_subscriber = my_robot_agent.simple_subscriber:main',
        'decision_agent = my_robot_agent.decision_agent:main',
    ],
},
```

## Running the Decision Agent

### 1. Rebuild the Package
```bash
cd ~/ros2_ws
colcon build --packages-select my_robot_agent
source install/setup.bash
```

### 2. Run the Agent
```bash
ros2 run my_robot_agent decision_agent
```

### 3. Simulate Sensor Data
In another terminal:
```bash
# Send sensor data with obstacles
ros2 topic pub /sensor_data std_msgs/String "data: 'obstacle detected ahead'"
```

## Basic URDF Robot Model

Create a simple URDF model for a wheeled robot in `~/ros2_ws/src/my_robot_agent/urdf/simple_robot.urdf`:

```xml
<?xml version="1.0"?>
<robot name="simple_robot">
  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.3 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 0.8"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.3 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Left Wheel -->
  <link name="left_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 0.8"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Right Wheel -->
  <link name="right_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 0.8"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Joints -->
  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 0.2 -0.1" rpy="1.5708 0 0"/>
  </joint>

  <joint name="right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0 -0.2 -0.1" rpy="1.5708 0 0"/>
  </joint>
</robot>
```

## Validating Your URDF Model

### 1. Check URDF Syntax
```bash
# Install robot model tools if not already installed
sudo apt install ros-humble-robot-state-publisher ros-humble-joint-state-publisher

# Validate the URDF
check_urdf ~/ros2_ws/src/my_robot_agent/urdf/simple_robot.urdf
```

### 2. Visualize the Robot Model
```bash
# Launch robot state publisher with your URDF
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:=$(cat ~/ros2_ws/src/my_robot_agent/urdf/simple_robot.urdf)
```

## Next Steps

Congratulations! You've successfully:
1. Set up a ROS 2 environment
2. Created and run publisher/subscriber nodes
3. Built a simple decision-making agent
4. Created a basic URDF robot model

In the full module, you'll learn about:
- Advanced ROS 2 communication patterns (services, actions)
- More complex URDF models for humanoid robots
- Integration of AI agents with ROS 2 systems
- Simulation environments for testing

Continue to the next chapters to deepen your understanding of ROS 2 concepts and their applications in robotics and AI.