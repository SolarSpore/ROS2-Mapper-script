#!/usr/bin/env python3
"""
Convenience launch file for starting the standard ROS 2 `joy` package's
joy_node, which publishes controller input as sensor_msgs/msg/Joy on /joy.

joy_node itself ships with ROS 2 (package: joy) and is not custom code —
this file just wraps `ros2 run joy joy_node` so it can be launched
alongside other nodes if desired.

Usage:
    ros2 launch scripts/joy_node.launch.py
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen',
        ),
    ])
