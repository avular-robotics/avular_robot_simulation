# Copyright 2026 Avular Holding B.V.
# All Rights Reserved
# You may use this code under the terms of the Avular
# Software End-User License Agreement.
#
# You should have received a copy of the Avular
# Software End-User License Agreement license with
# this file, or download it from: avular.com/eula

import math
import random

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.duration import Duration

from std_srvs.srv import Trigger
from std_msgs.msg import Bool, UInt8, Float64
from sensor_msgs.msg import NavSatFix, Image, CameraInfo
from nav_msgs.msg import Odometry
from avular_origin_msgs.msg import (
    BatteryInfo,
    CollisionAvoidanceMode,
    GNSSStatus,
    InitialHeading,
    LongitudalVelocityLimits,
    NetworkTelemetry,
)

class OriginTopics(Node):

    def __init__(self):
        super().__init__('avular_specific_topics')
        tf_prefix = self.declare_parameter('tf_prefix', '').get_parameter_value().string_value
        self._frame_prefix = f"{tf_prefix}_" if tf_prefix else ""

        # emergency brake
        self.publisher_ebrake = self.create_publisher(Bool, 'safety_supervisor/emergency_brake_active', 10)
        timer_period = 1.0  # seconds 
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.emergency_brake = Bool()

        # battery info
        self.publisher_battery = self.create_publisher(BatteryInfo, 'battery/info', 10)
        self.battery_info = BatteryInfo()
        self.battery_info.voltage = 50.0        # V (fixed)
        self.battery_info.state_of_charge = 100  # % of charge remaining (fixed)

        # mode of operation
        self.publisher_mode = self.create_publisher(UInt8, 'mode_of_operation', 10)
        self.mode_of_operation = UInt8()
        self.mode_of_operation.data = 1  # fixed: always ready

        # longitudinal velocity limits (fixed +-1.5 m/s)
        self.publisher_velocity_limits = self.create_publisher(
            LongitudalVelocityLimits, 'safety_supervisor/velocity_limits', 10)
        self.velocity_limits = LongitudalVelocityLimits()
        self.velocity_limits.max_forward_velocity = 1.5
        self.velocity_limits.max_backward_velocity = -1.5

        # network telemetry (fixed: no network in sim).
        self.publisher_network = self.create_publisher(
            NetworkTelemetry, 'origin_network_telemetry/network', 10)
        self.network_telemetry = NetworkTelemetry()
        self.network_telemetry.cellular_strength = NetworkTelemetry.CELLULAR_STRENGTH_UNKNOWN  # -1
        self.network_telemetry.cellular_operator = 'UNKNOWN'
        self.network_telemetry.wifi_strength = NetworkTelemetry.WIFI_STRENGTH_UNKNOWN  # -1
        self.network_telemetry.wifi_ssid = 'Origin mocks'
        self.network_telemetry.wifi_ip = '192.168.0.1'
        self.network_timer = self.create_timer(300.0, self.network_callback)

        # initial heading: robot spwans looking at North; drawn once at startup in [0, pi/4] to reflect unreliability of magenotemeter
        self.publisher_initial_heading = self.create_publisher(InitialHeading, 'initial_heading', 10)
        self.initial_heading = InitialHeading()
        self.initial_heading.initial_heading_rads = random.uniform(0.0, math.pi / 4)

        # create publisher for mocking the GNSS status. On a fresh valid fix we
        # report nominal quality; on loss of fix we mirror the real robot
        # (NO_FIX, 0 satellites, NaN accuracy). All set each tick in the timer.
        self.publisher_gnss_status = self.create_publisher(GNSSStatus, 'gnss/status', 10)
        self.gnss_status = GNSSStatus()
        self.gnss_status.header.frame_id = f'{self._frame_prefix}gnss_link'
        self.gnss_good_status = GNSSStatus.STATUS_RTK_FIX  # healthy fix quality
        # nominal quality reported while a valid fix is present
        self.gnss_h_accuracy = 0.02  # m, 1-sigma
        self.gnss_v_accuracy = 0.03  # m, 1-sigma
        self.gnss_sats_visible = 20
        self.gnss_sats_used = 18

        # react to real fix presence on gnss/fix (drives status + stamp)
        self.last_fix = None
        self.last_fix_time = None
        self.gnss_fix_timeout = Duration(seconds=1.0)  # NavSat ~10 Hz -> 1 s = ~10 missed msgs
        self.subscription_fix = self.create_subscription(
            NavSatFix, 'gnss/fix', self.gnss_fix_callback, 10)

        # odometer: seconds running (sim time from odom stamps) and metres driven
        self.publisher_s_running = self.create_publisher(Float64, 'odometer/s_running', 10)
        self.publisher_m_driven = self.create_publisher(Float64, 'odometer/m_driven', 10)
        self.s_running_msg = Float64()
        self.m_driven_msg = Float64()
        self.meters_driven = 0.0
        self.last_odom_xy = None
        self.odom_start_time = None   # float sec, first odom stamp (sim time)
        self.odom_latest_time = None  # float sec, most recent odom stamp
        self.subscription_odom = self.create_subscription(
            Odometry, 'odom', self.odom_callback, 10)
        self.odometer_timer = self.create_timer(10.0, self.odometer_callback)  # 0.1 Hz

        # collision avoidance mode: published manually, no functionality here;
        # only validates that a known mode (0-3) is passed.
        self.subscription_collision = self.create_subscription(
            CollisionAvoidanceMode, 'set_collision_avoidance',
            self.set_collision_avoidance_callback, 10)



    def timer_callback(self):
        self.emergency_brake.data = False
        self.publisher_ebrake.publish(self.emergency_brake)

        self.publisher_battery.publish(self.battery_info)

        self.publisher_mode.publish(self.mode_of_operation)

        self.publisher_initial_heading.publish(self.initial_heading)

        self.publisher_velocity_limits.publish(self.velocity_limits)

        now = self.get_clock().now()
        fresh = (
            self.last_fix is not None
            and (now - self.last_fix_time) <= self.gnss_fix_timeout
        )
        if fresh and self.last_fix.status.status >= 0:  # NavSatStatus.STATUS_NO_FIX == -1
            self.gnss_status.status = self.gnss_good_status
            self.gnss_status.satellites_visible = self.gnss_sats_visible
            self.gnss_status.satellites_used = self.gnss_sats_used
            self.gnss_status.horizontal_position_accuracy = self.gnss_h_accuracy
            self.gnss_status.vertical_position_accuracy = self.gnss_v_accuracy
            self.gnss_status.header.stamp = self.last_fix.header.stamp  # sim-time, aligned to fix
        else:
            self.gnss_status.status = GNSSStatus.STATUS_NO_FIX
            self.gnss_status.satellites_visible = 0  # no fix -> no sats
            self.gnss_status.satellites_used = 0
            self.gnss_status.horizontal_position_accuracy = math.nan  # undefined on no fix
            self.gnss_status.vertical_position_accuracy = math.nan
            self.gnss_status.header.stamp = now.to_msg()
        self.publisher_gnss_status.publish(self.gnss_status)
        #self.get_logger().info('Publishing: "%s"' % msg.data)

    def gnss_fix_callback(self, msg):
        self.last_fix = msg
        self.last_fix_time = self.get_clock().now()

    def odom_callback(self, msg):
        # metres: accumulate 2D translation
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        if self.last_odom_xy is not None:
            self.meters_driven += math.dist(self.last_odom_xy, (x, y))
        self.last_odom_xy = (x, y)

        # seconds: sim time carried in the odom header stamp
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        if self.odom_start_time is None:
            self.odom_start_time = t
        self.odom_latest_time = t

    def odometer_callback(self):
        if self.odom_start_time is not None:
            self.s_running_msg.data = self.odom_latest_time - self.odom_start_time
        self.publisher_s_running.publish(self.s_running_msg)

        self.m_driven_msg.data = self.meters_driven
        self.publisher_m_driven.publish(self.m_driven_msg)

    def set_collision_avoidance_callback(self, msg):
        valid_modes = (
            CollisionAvoidanceMode.USE_ALL_ULTRASONIC_SENSORS,    # 0
            CollisionAvoidanceMode.USE_FRONT_ULTRASONIC_SENSORS,  # 1
            CollisionAvoidanceMode.USE_BACK_ULTRASONIC_SENSORS,   # 2
            CollisionAvoidanceMode.DISABLE_COLLISION_AVOIDANCE,   # 3
        )
        if msg.mode not in valid_modes:
            self.get_logger().warn(
                f'set_collision_avoidance: invalid mode {msg.mode} (valid: 0-3)')

    def network_callback(self):
        self.publisher_network.publish(self.network_telemetry)


def main(args=None):
    rclpy.init(args=args)

    avular_specific_topics = OriginTopics()

    try:
        rclpy.spin(avular_specific_topics)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        avular_specific_topics.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
