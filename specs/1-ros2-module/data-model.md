# Data Model: Module 1 — The Robotic Nervous System (ROS 2)

## Core Entities

### 1. ROS 2 Node
**Description**: An independent process that communicates with other nodes using topics, services, actions, and parameters.

**Fields**:
- `node_id`: string (unique identifier for the node)
- `node_name`: string (name of the node in the ROS graph)
- `namespace`: string (optional namespace for the node)
- `parameters`: map<string, variant> (node parameters)
- `publishers`: list<Publisher> (list of publishers created by the node)
- `subscribers`: list<Subscriber> (list of subscribers created by the node)
- `services`: list<Service> (list of services provided by the node)
- `clients`: list<Client> (list of service clients created by the node)
- `actions`: list<Action> (list of action servers/clients)

**Relationships**:
- One-to-Many: A node can have multiple publishers, subscribers, services, etc.
- Many-to-Many: Nodes communicate with each other through topics and services

**Validation Rules**:
- Node name must be unique within the ROS graph
- Node name must follow ROS naming conventions (alphanumeric, underscores, forward slashes)
- Node must have at least one communication interface (publisher, subscriber, service, etc.)

### 2. ROS 2 Topic
**Description**: A communication channel where nodes publish data that other nodes can subscribe to.

**Fields**:
- `topic_name`: string (name of the topic)
- `topic_type`: string (message type, e.g., std_msgs/msg/String)
- `publishers`: list<Publisher> (nodes publishing to this topic)
- `subscribers`: list<Subscriber> (nodes subscribed to this topic)
- `qos_profile`: QoSProfile (quality of service settings)

**Relationships**:
- Many-to-Many: Multiple nodes can publish and subscribe to the same topic
- One-to-Many: One topic can have multiple publishers and subscribers

**Validation Rules**:
- Topic name must follow ROS naming conventions
- Topic type must be a valid ROS message type
- Publishers and subscribers must agree on message type

### 3. ROS 2 Service
**Description**: A request-response communication pattern between nodes.

**Fields**:
- `service_name`: string (name of the service)
- `service_type`: string (service type, e.g., std_srvs/srv/SetBool)
- `server`: Node (the node providing the service)
- `clients`: list<Node> (nodes that call this service)
- `qos_profile`: QoSProfile (quality of service settings)

**Relationships**:
- One-to-Many: One service server can have multiple clients
- Many-to-One: Multiple clients can call the same service

**Validation Rules**:
- Service name must follow ROS naming conventions
- Service type must be a valid ROS service type
- Only one server per service name

### 4. ROS 2 Message
**Description**: The data structure used for communication between nodes via topics or services.

**Fields**:
- `message_type`: string (fully qualified message type)
- `fields`: list<MessageField> (list of fields in the message)
- `timestamp`: datetime (when the message was created)
- `data`: variant (the actual message content)

**Relationships**:
- One-to-Many: One message type can be used by many messages
- Many-to-One: Many messages can be sent via one topic

**Validation Rules**:
- Message fields must match the defined message type schema
- Required fields must be present
- Field types must match the schema definition

### 5. Python Agent
**Description**: A Python program that uses rclpy to interact with ROS 2 systems, typically implementing AI/ML decision-making.

**Fields**:
- `agent_id`: string (unique identifier for the agent)
- `agent_name`: string (display name for the agent)
- `node_handle`: Node (the ROS 2 node used by the agent)
- `input_topics`: list<Topic> (topics the agent subscribes to)
- `output_topics`: list<Topic> (topics the agent publishes to)
- `services_used`: list<Service> (services the agent calls)
- `behavior_logic`: string (path to the agent's decision-making code)
- `state`: AgentState (current state of the agent)

**Relationships**:
- One-to-One: Each agent has one ROS 2 node
- Many-to-Many: Agents can connect to multiple topics and services

**Validation Rules**:
- Agent must have a valid ROS 2 node connection
- Input and output topics must exist in the ROS graph
- Agent behavior logic must be valid Python code

### 6. URDF Model
**Description**: Unified Robot Description Format file that defines robot structure, kinematics, and dynamics.

**Fields**:
- `model_id`: string (unique identifier for the model)
- `model_name`: string (name of the robot model)
- `links`: list<URDFLink> (list of rigid body links)
- `joints`: list<URDFJoint> (list of joints connecting links)
- `materials`: list<URDFMaterial> (list of materials used)
- `transmissions`: list<URDFTransmission> (list of transmission elements)
- `gazebo_extensions`: list<GazeboExtension> (Gazebo-specific extensions)
- `file_path`: string (path to the URDF file)

**Relationships**:
- One-to-Many: One model contains multiple links, joints, etc.
- Many-to-One: Multiple joints connect different links

**Validation Rules**:
- URDF must be well-formed XML
- All referenced links in joints must exist
- No circular dependencies in joint connections
- Mass and inertia properties must be positive

### 7. URDF Link
**Description**: A rigid body element in a URDF robot model.

**Fields**:
- `link_name`: string (name of the link)
- `visual`: VisualGeometry (visual representation for graphics)
- `collision`: CollisionGeometry (collision representation for physics)
- `inertial`: InertialProperties (mass and inertia properties)
- `parent_joint`: URDFJoint (joint that connects to parent, null for root)

**Relationships**:
- One-to-Many: One link can have visual, collision, and inertial properties
- Many-to-One: Multiple links connect through joints

**Validation Rules**:
- Link name must be unique within the model
- Inertial properties must be physically valid (positive mass, valid inertia tensor)

### 8. URDF Joint
**Description**: Connection between two links in a URDF robot model.

**Fields**:
- `joint_name`: string (name of the joint)
- `joint_type`: JointType (type of joint: revolute, continuous, prismatic, etc.)
- `parent_link`: URDFLink (parent link in the kinematic chain)
- `child_link`: URDFLink (child link in the kinematic chain)
- `origin`: Transform (transform from parent to child)
- `axis`: Vector3 (rotation or translation axis)
- `limits`: JointLimits (joint limits for revolute/prismatic joints)

**Relationships**:
- Many-to-One: Multiple joints can have the same parent or child link
- One-to-One: Each joint connects exactly two links

**Validation Rules**:
- Parent and child links must exist in the model
- Joint type must be valid (revolute, continuous, prismatic, fixed, etc.)
- Joint limits must be consistent with joint type

## State Transitions

### Node State Transitions
- `UNCONFIGURED` → `INACTIVE`: Node is configured but not activated
- `INACTIVE` → `ACTIVE`: Node is activated and ready to process data
- `ACTIVE` → `INACTIVE`: Node is deactivated but still configured
- `ACTIVE/INACTIVE` → `FINALIZED`: Node is shut down

### Agent State Transitions
- `INITIALIZING` → `READY`: Agent is set up and waiting for input
- `READY` → `PROCESSING`: Agent is processing input and making decisions
- `PROCESSING` → `READY`: Agent completed processing
- `PROCESSING` → `ERROR`: Agent encountered an error
- `ERROR` → `READY`: Agent recovered from error

## API Contracts

### ROS 2 Node Interface
```
class Node:
    def create_publisher(self, msg_type, topic_name, qos_profile) -> Publisher
    def create_subscription(self, msg_type, topic_name, callback, qos_profile) -> Subscriber
    def create_service(self, srv_type, srv_name, callback) -> Service
    def create_client(self, srv_type, srv_name) -> Client
```

### Python Agent Interface
```
class PythonAgent:
    def initialize(self) -> bool
    def connect_to_ros(self) -> bool
    def process_sensor_data(self, sensor_data) -> Action
    def publish_action(self, action) -> bool
    def shutdown(self) -> bool
```

### URDF Validation Interface
```
class URDFValidator:
    def validate_model(self, urdf_path) -> ValidationResult
    def check_kinematic_chain(self, urdf_model) -> bool
    def validate_inertial_properties(self, urdf_model) -> bool
```

## Data Flow Patterns

### Sensor Data Flow
1. Physical sensors collect data
2. Sensor drivers publish to ROS topics
3. Python agent subscribes to sensor topics
4. Agent processes data and makes decisions
5. Agent publishes commands to actuator topics

### Control Command Flow
1. Python agent decides on actions
2. Agent publishes commands to ROS topics
3. Controller nodes subscribe to command topics
4. Controllers send commands to physical actuators
5. Feedback loop through sensor data

### Model Loading Flow
1. URDF file is loaded by robot state publisher
2. TF tree is constructed from URDF joints
3. Visualization tools display robot model
4. Simulation engines use model for physics
5. Planning algorithms use model for kinematics