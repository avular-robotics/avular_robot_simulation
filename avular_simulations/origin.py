# Copyright 2026 Avular Holding B.V.
# All Rights Reserved
# You may use this code under the terms of the Avular
# Software End-User License Agreement.
#
# You should have received a copy of the Avular
# Software End-User License Agreement license with
# this file, or download it from: avular.com/eula

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from origin_one_description.launch_helpers import (
    launch_robot_state_publisher as launch_origin_state_publisher,
)
from origin_one_description.launch_helpers import launch_rviz as launch_origin_rviz

from avular_simulations.bridges import launch_parameter_bridge
from avular_simulations.spawn import spawn_robot


# Sensor sub-frames that exist on hardware (published at runtime by the
# realsense2_camera and ouster drivers) but not in the robot URDF. In simulation
# we stand in for those drivers and broadcast them so /tf_static matches the
# real robot.
# Tuples: (x, y, z, qx, qy, qz, qw, parent, child) -- frame names get tf_prefix.
_SENSOR_STATIC_TFS = [
    # RealSense D435: color frame carries the ~14.7 mm RGB-vs-depth baseline;
    # the optical frames use the standard body->optical-frame rotation.
    ("0", "0.0147", "0", "0", "0", "0", "1", "camera_link", "camera_color_frame"),
    ("0", "0", "0", "-0.5", "0.5", "-0.5", "0.5", "camera_color_frame", "camera_color_optical_frame"),
    ("0", "0", "0", "0", "0", "0", "1", "camera_link", "camera_depth_frame"),
    ("0", "0", "0", "-0.5", "0.5", "-0.5", "0.5", "camera_depth_frame", "camera_depth_optical_frame"),
    # Ouster OS1-32: datasheet offsets from os_sensor; os_lidar is yawed 180 deg.
    ("0.006253", "-0.011775", "0.007645", "0", "0", "0", "1", "os_sensor", "os_imu"),
    ("0", "0", "0.03618", "0", "0", "1", "0", "os_sensor", "os_lidar"),
]


def _sensor_static_tfs(context):
    prefix = LaunchConfiguration("tf_prefix").perform(context)
    p = f"{prefix}_" if prefix else ""
    nodes = []
    for x, y, z, qx, qy, qz, qw, parent, child in _SENSOR_STATIC_TFS:
        nodes.append(
            Node(
                package="tf2_ros",
                executable="static_transform_publisher",
                name=f"tf_static_{parent}_to_{child}",
                arguments=[
                    "--x", x, "--y", y, "--z", z,
                    "--qx", qx, "--qy", qy, "--qz", qz, "--qw", qw,
                    "--frame-id", f"{p}{parent}",
                    "--child-frame-id", f"{p}{child}",
                ],
            )
        )
    return nodes


def spawn_origin(ld: LaunchDescription):
    """Bring the Avular Origin online in the running Gazebo world: spawn
    the sim URDF, run robot_state_publisher off the description package,
    bridge ROS/Gazebo topics and rviz + the cmd_vel_controller.
    """
    pkg_share = get_package_share_directory("avular_simulations")
    xacro_file = os.path.join(pkg_share, "urdf", "origin_sim.urdf.xacro")

    spawn_robot(
        ld,
        xacro_file=xacro_file,
        robot_name=LaunchConfiguration("robot_name"),
        ns=LaunchConfiguration("ns"),
        tf_prefix=LaunchConfiguration("tf_prefix"),
        pose_x=LaunchConfiguration("robot_pose_x"),
        pose_y=LaunchConfiguration("robot_pose_y"),
        pose_yaw=LaunchConfiguration("robot_pose_yaw"),
        drive_configuration=LaunchConfiguration("drive_configuration"),
        spawn=LaunchConfiguration("spawn"),
    )

    launch_parameter_bridge(
        ld,
        config_template=LaunchConfiguration("bridge_config"),
        robot_name=LaunchConfiguration("robot_name"),
        ns=LaunchConfiguration("ns"),
        spawn=LaunchConfiguration("spawn"),
    )

    launch_origin_state_publisher(
        ld,
        drive_configuration=LaunchConfiguration("drive_configuration"),
        ns=LaunchConfiguration("ns"),
        tf_prefix=LaunchConfiguration("tf_prefix"),
    )

    ld.add_action(OpaqueFunction(function=_sensor_static_tfs))

    ld.add_action(
        Node(
            package="avular_simulations",
            executable="origin_mocks",
            namespace=["/", LaunchConfiguration("ns")],
            parameters=[{"tf_prefix": LaunchConfiguration("tf_prefix")}],
            output="screen",
        )
    )

    ld.add_action(
        Node(
            package="avular_cmd_vel_controller",
            executable="cmd_vel_controller",
            name="cmd_vel_controller",
            namespace=LaunchConfiguration("ns"),
            parameters=[
                os.path.join(pkg_share, "config", "origin", "cmd_vel_controller.yaml")
            ],
            respawn=True,
            respawn_delay=1.0,
            condition=IfCondition(LaunchConfiguration("use_cmd_vel_controller")),
        )
    )

    ld.add_action(
        Node(
            package="joy",
            executable="joy_node",
            name="joy_node",
            namespace=LaunchConfiguration("ns"),
            parameters=[{"device_id": 0, "deadzone": 0.05}],
            respawn=True,
            respawn_delay=2.0,
            condition=IfCondition(LaunchConfiguration("use_joy")),
        )
    )

    # No respawn: joy_interpreter throws if the Joy message carries fewer buttons than its
    # mapping expects, and a respawn loop would bury that in the launch log.
    ld.add_action(
        Node(
            package="avular_joy_interpreter",
            executable="joy_interpreter",
            name="joy_interpreter",
            namespace=LaunchConfiguration("ns"),
            parameters=[
                os.path.join(pkg_share, "config", "origin", "joy_interpreter.yaml")
            ],
            output="screen",
            condition=IfCondition(LaunchConfiguration("use_joy")),
        )
    )

    launch_origin_rviz(
        ld,
        ns=LaunchConfiguration("ns"),
        tf_prefix=LaunchConfiguration("tf_prefix"),
        condition=IfCondition(LaunchConfiguration("rviz")),
    )
