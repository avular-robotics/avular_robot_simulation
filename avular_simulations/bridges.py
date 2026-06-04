# Copyright 2026 Avular Holding B.V.
# All Rights Reserved
# You may use this code under the terms of the Avular
# Software End-User License Agreement.
#
# You should have received a copy of the Avular
# Software End-User License Agreement license with
# this file, or download it from: avular.com/eula

import os
import tempfile

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import OpaqueFunction
from launch.conditions import IfCondition
from launch_ros.actions import Node


def launch_parameter_bridge(
    ld: LaunchDescription,
    config_template,
    robot_name="robot",
    ns="robot",
    spawn="true",
    log_level: str = "warn",
):
    """Render the ros_gz_bridge parameter_bridge config template, replacing
    /robot with /<ns>, write it to a temp file, and add a
    parameter_bridge Node referencing it.
    """
    pkg_share = get_package_share_directory("avular_simulations")

    def _make_bridge(context):
        ns_value = ns.perform(context) if hasattr(ns, "perform") else str(ns)
        name_value = (
            robot_name.perform(context)
            if hasattr(robot_name, "perform")
            else str(robot_name)
        )
        template_value = (
            config_template.perform(context)
            if hasattr(config_template, "perform")
            else str(config_template)
        )
        template_path = os.path.join(pkg_share, "config", template_value)
        with open(template_path, "r") as f:
            rendered = f.read().replace("/robot", f"/{ns_value}")
        fd, out_path = tempfile.mkstemp(prefix=f"{ns_value}_bridge_", suffix=".yaml")
        with os.fdopen(fd, "w") as f:
            f.write(rendered)

        node_name = f"{name_value}_gz_bridge"
        return [
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name=node_name,
                output="screen",
                parameters=[
                    {
                        "config_file": out_path,
                        f"qos_overrides./{ns_value}/cmd_vel.subscription.reliability": "best_effort",
                    }
                ],
                arguments=[
                    "--ros-args",
                    "--log-level",
                    f"{node_name}:={log_level}",
                ],
            )
        ]

    ld.add_action(OpaqueFunction(function=_make_bridge, condition=IfCondition(spawn)))
