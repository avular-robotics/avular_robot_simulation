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
from avular_simulations.server import start_world


def generate_launch_description():
    ld = LaunchDescription()

    ld.add_action(
        DeclareLaunchArgument("world", default_value="avular_testing_area.world")
    )
    ld.add_action(DeclareLaunchArgument("headless", default_value="false"))
    ld.add_action(DeclareLaunchArgument("launch_world", default_value="true"))

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

    return ld
