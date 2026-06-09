# Copyright 2026 Avular Holding B.V.
# All Rights Reserved
# You may use this code under the terms of the Avular
# Software End-User License Agreement.
#
# You should have received a copy of the Avular
# Software End-User License Agreement license with
# this file, or download it from: avular.com/eula

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from avular_simulations.gui import start_gui
from avular_simulations.origin import spawn_origin
from avular_simulations.server import start_world


def generate_launch_description():
    ld = LaunchDescription()

    ld.add_action(DeclareLaunchArgument("headless", default_value="false"))
    ld.add_action(DeclareLaunchArgument("launch_world", default_value="true"))
    ld.add_action(DeclareLaunchArgument("spawn", default_value="true"))
    ld.add_action(DeclareLaunchArgument("robot_name", default_value="origin"))
    ld.add_action(DeclareLaunchArgument("ns", default_value="robot"))
    ld.add_action(DeclareLaunchArgument("tf_prefix", default_value=""))
    ld.add_action(
        DeclareLaunchArgument("world", default_value="avular_testing_area.world")
    )
    ld.add_action(
        DeclareLaunchArgument(
            "drive_configuration", default_value="skid_steer_drive"
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            "bridge_config", default_value="origin/gazebo_ros_bridge.yaml"
        )
    )
    ld.add_action(
        DeclareLaunchArgument("use_cmd_vel_controller", default_value="False")
    )
    ld.add_action(DeclareLaunchArgument("robot_pose_x", default_value="-19.0"))
    ld.add_action(DeclareLaunchArgument("robot_pose_y", default_value="-36.0"))
    ld.add_action(DeclareLaunchArgument("robot_pose_yaw", default_value="1.57"))
    ld.add_action(
        DeclareLaunchArgument(
            "rviz",
            default_value="false",
            description="Launch RViz pre-configured for this robot's namespace/prefix.",
        )
    )

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
    spawn_origin(ld)

    return ld
