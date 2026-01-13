"""
Sample test queries for book-related topics to simulate real user questions
"""

# ROS2 related queries
ROS2_QUERIES = [
    "What is ROS2 and how does it differ from ROS1?",
    "Explain the concept of ROS2 nodes and their communication",
    "How do I create a ROS2 package?",
    "What are ROS2 topics and services?",
    "How to use ROS2 launch files?",
    "Explain ROS2 parameters and their usage",
    "What is the ROS2 middleware layer?",
    "How to debug ROS2 applications?",
    "What are ROS2 actions and how to use them?",
    "Explain ROS2 security features"
]

# Gazebo related queries
GAZEBO_QUERIES = [
    "How to create a robot model for Gazebo simulation?",
    "What are SDF files and how to write them?",
    "How to add sensors to a Gazebo robot model?",
    "Explain Gazebo plugins and their types",
    "How to control a robot in Gazebo simulation?",
    "What are Gazebo worlds and how to create them?",
    "How to use Gazebo ROS interfaces?",
    "Explain physics engines in Gazebo",
    "How to add lighting and textures to Gazebo models?",
    "What are Gazebo controllers?"
]

# Isaac Sim related queries
ISAAC_SIM_QUERIES = [
    "How to set up Isaac Sim for robotics simulation?",
    "What are USD files in Isaac Sim?",
    "How to create robot assets in Isaac Sim?",
    "Explain Isaac Sim extensions and their usage",
    "How to use Isaac Sim for AI training?",
    "What are Omniverse Nucleus and its role?",
    "How to control robots in Isaac Sim?",
    "Explain Isaac Sim sensors and their configuration",
    "How to create synthetic data with Isaac Sim?",
    "What are Isaac Sim tasks and workflows?"
]

# VLA (Vision-Language-Action) related queries
VLA_QUERIES = [
    "What is Vision-Language-Action (VLA) in robotics?",
    "How do VLA models understand natural language commands?",
    "Explain the architecture of VLA models",
    "How to train VLA models for robotics tasks?",
    "What are the challenges in VLA robotics?",
    "How do VLA models process visual information?",
    "Explain grounding language to actions in VLA",
    "What datasets are used for VLA training?",
    "How to evaluate VLA model performance?",
    "What are the applications of VLA in robotics?"
]

# General robotics queries
GENERAL_QUERIES = [
    "What is the difference between forward and inverse kinematics?",
    "How does path planning work in robotics?",
    "Explain SLAM in robotics applications",
    "What are the different types of robot actuators?",
    "How do robot sensors work and what types exist?",
    "What is robot operating system (ROS) used for?",
    "Explain robot perception in AI",
    "How do robots navigate in unknown environments?",
    "What are the safety considerations in robotics?",
    "How do robots learn from demonstrations?"
]

# All test queries combined
ALL_TEST_QUERIES = (
    ROS2_QUERIES +
    GAZEBO_QUERIES +
    ISAAC_SIM_QUERIES +
    VLA_QUERIES +
    GENERAL_QUERIES
)

# Predefined validation queries
PREDEFINED_QUERIES = [
    "What is ROS2?",
    "Explain Gazebo simulation",
    "How to use Isaac Sim?",
    "What are VLA models?",
    "How does robot perception work?",
    "Explain SLAM in robotics",
    "What are ROS2 nodes?",
    "How to create robot models?",
    "What is path planning?",
    "How do robot sensors work?"
]