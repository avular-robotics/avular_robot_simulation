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
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

from vertex_one_description.launch_helpers import (
    launch_robot_state_publisher as launch_vertex_state_publisher,
)
from vertex_one_description.launch_helpers import launch_rviz as launch_vertex_rviz

from avular_simulations.bridges import launch_parameter_bridge
from avular_simulations.spawn import spawn_robot


def spawn_vertex(ld: LaunchDescription):
    """Bring the Avular Vertex online in the running Gazebo world: spawn the
    sim URDF, run robot_state_publisher off the description package, bridge
    ROS/Gazebo topics, and (optionally) rviz.
    """
    pkg_share = get_package_share_directory("avular_simulations")
    xacro_file = os.path.join(pkg_share, "urdf", "vertex_sim.urdf.xacro")

    spawn_robot(
        ld,
        xacro_file=xacro_file,
        robot_name=LaunchConfiguration("robot_name"),
        ns=LaunchConfiguration("ns"),
        tf_prefix=LaunchConfiguration("tf_prefix"),
        pose_x=LaunchConfiguration("robot_pose_x"),
        pose_y=LaunchConfiguration("robot_pose_y"),
        pose_z=LaunchConfiguration("robot_pose_z"),
        pose_yaw=LaunchConfiguration("robot_pose_yaw"),
        spawn=LaunchConfiguration("spawn"),
    )

    launch_parameter_bridge(
        ld,
        config_template=LaunchConfiguration("bridge_config"),
        robot_name=LaunchConfiguration("robot_name"),
        ns=LaunchConfiguration("ns"),
        spawn=LaunchConfiguration("spawn"),
    )

    launch_vertex_state_publisher(
        ld,
        ns=LaunchConfiguration("ns"),
        tf_prefix=LaunchConfiguration("tf_prefix"),
    )

    launch_vertex_rviz(
        ld,
        ns=LaunchConfiguration("ns"),
        tf_prefix=LaunchConfiguration("tf_prefix"),
        condition=IfCondition(LaunchConfiguration("rviz")),
    )
