# Copyright 2026 Avular Holding B.V.
# All Rights Reserved
# You may use this code under the terms of the Avular
# Software End-User License Agreement.
#
# You should have received a copy of the Avular
# Software End-User License Agreement license with
# this file, or download it from: avular.com/eula

import xacro
from launch import LaunchDescription
from launch.actions import OpaqueFunction, SetLaunchConfiguration
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def spawn_robot(
    ld: LaunchDescription,
    xacro_file: str,
    robot_name="robot",
    ns="robot",
    tf_prefix="",
    pose_x="0.0",
    pose_y="0.0",
    pose_z="1.0",
    pose_yaw="0.0",
    drive_configuration=None,
    spawn="true",
    log_level: str = "warn",
):
    """Process the simulation xacro and run ``ros_gz_sim create`` to spawn
    the resulting URDF at the given pose. The xacro is rendered with
    ``namespace`` and ``prefix`` mappings (and ``drive_configuration`` when
    provided) so it matches what the description package's RSP sees.
    """

    def _process_xacro(context):
        mappings = {
            "prefix": (
                tf_prefix.perform(context)
                if hasattr(tf_prefix, "perform")
                else str(tf_prefix)
            ),
            "namespace": (
                ns.perform(context) if hasattr(ns, "perform") else str(ns)
            ),
        }
        if drive_configuration is not None:
            mappings["drive_configuration"] = (
                drive_configuration.perform(context)
                if hasattr(drive_configuration, "perform")
                else str(drive_configuration)
            )
        urdf = xacro.process_file(xacro_file, mappings=mappings).toxml()
        return [SetLaunchConfiguration("urdf", urdf)]

    ld.add_action(OpaqueFunction(function=_process_xacro))
    ld.add_action(
        Node(
            package="ros_gz_sim",
            executable="create",
            arguments=[
                "-name", robot_name,
                "-string", LaunchConfiguration("urdf"),
                "-x", pose_x,
                "-y", pose_y,
                "-z", pose_z,
                "-Y", pose_yaw,
                "--ros-args",
                "--log-level",
                f"create:={log_level}",
            ],
            output="screen",
            condition=IfCondition(spawn),
        )
    )
