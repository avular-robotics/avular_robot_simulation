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
from launch.actions import ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import AndSubstitution, NotSubstitution


def start_gui(
    ld: LaunchDescription,
    headless="false",
    launch_world="true",
    verbosity: str = "1",
    gui_config: str = None,
):
    """Start the Gazebo GUI client; skipped when ``headless`` or when no
    server is being started by this launch (``launch_world`` is false).

    ``gui_config`` is the path to the ``.config`` GUI layout file; when not
    given it defaults to ``config/gui.config``.
    """
    if gui_config is None:
        gui_config = os.path.join(
            get_package_share_directory("avular_simulations"),
            "config",
            "gui.config",
        )

    ld.add_action(
        ExecuteProcess(
            cmd=["gz", "sim", "-g", f"-v{verbosity}", "--gui-config", gui_config],
            condition=IfCondition(
                AndSubstitution(launch_world, NotSubstitution(headless))
            ),
        )
    )
