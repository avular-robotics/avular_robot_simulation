# Copyright 2026 Avular Holding B.V.
# All Rights Reserved
# You may use this code under the terms of the Avular
# Software End-User License Agreement.
#
# You should have received a copy of the Avular
# Software End-User License Agreement license with
# this file, or download it from: avular.com/eula

import rclpy
from rclpy.node import Node

from std_srvs.srv import Trigger
from std_msgs.msg import Bool
from sensor_msgs.msg import NavSatFix, Image, CameraInfo

class AvularTopics(Node):

    def __init__(self):
        super().__init__('avular_specific_topics')
        # create publisher for 'faking' the emergency brake
        self.publisher_ebrake = self.create_publisher(Bool, 'safety_supervisor/emergency_brake_active', 10)
        timer_period = 1.0  # seconds 
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.emergency_brake = Bool()
        #create service
        self.srv = self.create_service(Trigger, 'set_obstacle_avoidance', self.set_avoidance_callback)

    def set_avoidance_callback(self, request, response):
        response.success = True
        #self.get_logger().info('setting obstacle avoidance to "%s"' % request.trigger)
        return response
    
    def timer_callback(self):
        self.emergency_brake.data = False
        self.publisher_ebrake.publish(self.emergency_brake)
        #self.get_logger().info('Publishing: "%s"' % msg.data)


def main(args=None):
    rclpy.init(args=args)

    avular_specific_topics = AvularTopics()

    rclpy.spin(avular_specific_topics)
    avular_specific_topics.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
