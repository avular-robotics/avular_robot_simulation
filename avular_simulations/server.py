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
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution


def start_world(
    ld: LaunchDescription,
    world_name="empty.world",
    launch_world="true",
    verbosity: str = "1",
):
    """Bring up the Gazebo server (headless) running the given world file."""
    pkg_share = get_package_share_directory("avular_simulations")
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")

    world_path = PathJoinSubstitution([pkg_share, "worlds", world_name])

    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")
            ),
            launch_arguments={
                "gz_args": [f"-r -s -v{verbosity} ", world_path],
                "gz_version": "6",
                "on_exit_shutdown": "true",
            }.items(),
            condition=IfCondition(launch_world),
        )
    )
