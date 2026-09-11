from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='table_perception',
            executable='color_detector',
            name='color_cube_detector',
            namespace='perception',
            parameters=[{
                'input_topic': '/perception/table_cam/color/image_raw',
                'output_topic': '/perception/detections',
                'debug_image_topic': '/perception/debug_image',
            }],
            output='screen',
        ),
    ])
