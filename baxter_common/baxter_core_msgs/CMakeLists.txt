cmake_minimum_required(VERSION 2.8.3)
project(baxter_core_msgs)

find_package(catkin REQUIRED COMPONENTS
  message_generation
  geometry_msgs
  sensor_msgs
  std_msgs
)

add_message_files(DIRECTORY msg FILES
  AnalogIOState.msg
  AnalogIOStates.msg
  AnalogOutputCommand.msg
  AssemblyState.msg
  AssemblyStates.msg
  CameraControl.msg
  CameraSettings.msg
  CollisionAvoidanceState.msg
  CollisionDetectionState.msg
  DigitalIOState.msg
  DigitalIOStates.msg
  DigitalOutputCommand.msg
  EndEffectorCommand.msg
  EndEffectorProperties.msg
  EndEffectorState.msg
  EndpointState.msg
  EndpointStates.msg
  HeadPanCommand.msg
  HeadState.msg
  JointCommand.msg
  NavigatorState.msg
  NavigatorStates.msg
  RobustControllerStatus.msg
  SEAJointState.msg
  URDFConfiguration.msg
  BridgePublisher.msg
)

add_service_files(DIRECTORY srv FILES
  CloseCamera.srv
  ListCameras.srv
  OpenCamera.srv
  SolvePositionIK.srv
  BridgePublishersAuth.srv
  BridgePublishersForce.srv
)

generate_messages(DEPENDENCIES
  geometry_msgs
  sensor_msgs
  std_msgs
)

catkin_package(CATKIN_DEPENDS
  message_runtime
  geometry_msgs
  sensor_msgs
  std_msgs
)
