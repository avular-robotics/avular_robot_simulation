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
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from avular_simulations.gui import start_gui
from avular_simulations.server import start_world


def generate_launch_description():
    ld = LaunchDescription()

    ld.add_action(
        DeclareLaunchArgument("world", default_value="avular_testing_area.world")
    )
    ld.add_action(DeclareLaunchArgument("headless", default_value="false"))
    ld.add_action(DeclareLaunchArgument("launch_world", default_value="true"))
    ld.add_action(DeclareLaunchArgument("rviz", default_value="false"))
    ld.add_action(DeclareLaunchArgument("origin_pose_x", default_value="-19.0"))
    ld.add_action(DeclareLaunchArgument("origin_pose_y", default_value="-36.0"))
    ld.add_action(DeclareLaunchArgument("origin_pose_yaw", default_value="1.57"))
    ld.add_action(DeclareLaunchArgument("vertex_pose_x", default_value="-17.0"))
    ld.add_action(DeclareLaunchArgument("vertex_pose_y", default_value="-36.0"))
    ld.add_action(DeclareLaunchArgument("vertex_pose_z", default_value="1.5"))
    ld.add_action(DeclareLaunchArgument("vertex_pose_yaw", default_value="0.0"))

    # Gazebo server + GUI, started once.
    start_world(
        ld,
        world_name=LaunchConfiguration("world"),
        launch_world=LaunchConfiguration("launch_world"),
    )
    start_gui(
        ld,
        headless=LaunchConfiguration("headless"),
        launch_world=LaunchConfiguration("launch_world"),
    )

    pkg_share = get_package_share_directory("avular_simulations")

    # Per-robot sim wrappers, each in its own launch scope so they see
    # their own ns/tf_prefix/pose values (note launch_world:=false to avoid
    # bringing up a second Gazebo server).
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_share, "launch", "origin_sim_common.launch.py")
            ),
            launch_arguments={
                "launch_world": "false",
                "robot_name": "origin",
                "ns": "origin",
                "tf_prefix": "origin",
                "bridge_config": "origin/gazebo_ros_bridge.yaml",
                "robot_pose_x": LaunchConfiguration("origin_pose_x"),
                "robot_pose_y": LaunchConfiguration("origin_pose_y"),
                "robot_pose_yaw": LaunchConfiguration("origin_pose_yaw"),
                "rviz": LaunchConfiguration("rviz"),
            }.items(),
        )
    )
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_share, "launch", "vertex_sim_common.launch.py")
            ),
            launch_arguments={
                "launch_world": "false",
                "robot_name": "vertex",
                "ns": "vertex",
                "tf_prefix": "vertex",
                "bridge_config": "vertex/gazebo_ros_bridge.yaml",
                "robot_pose_x": LaunchConfiguration("vertex_pose_x"),
                "robot_pose_y": LaunchConfiguration("vertex_pose_y"),
                "robot_pose_z": LaunchConfiguration("vertex_pose_z"),
                "robot_pose_yaw": LaunchConfiguration("vertex_pose_yaw"),
                "rviz": LaunchConfiguration("rviz"),
            }.items(),
        )
    )

    return ld
