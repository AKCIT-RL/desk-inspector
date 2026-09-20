# desk inspector

ros 2 (humble) perception system that detects colored cubes (red, yellow, green, purple) on a table using an intel realsense camera and hsv segmentation. it publishes detections as `vision_msgs/Detection2DArray` and a debug image with the bounding boxes drawn on it.

this is the first step of a larger application for monitoring and validating tasks performed by robotic platforms (tracking and validation are still to be discussed).

## prerequisites

- docker and docker compose
- intel realsense camera connected via usb
- linux with x11 (for `rqt_image_view`)
- nvidia gpu + [nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). without a gpu, remove the `deploy` block and the `NVIDIA_*` variables from `docker-compose.dev.yml`.

## how to run

```bash
# 1. allow access to the display (once per session)
xhost +local:docker

# 2. start the container and enter it
docker compose -f docker-compose.dev.yml up --build -d
docker exec -it desk_inspector_dev bash
```

inside the container:

```bash
# 3. build the workspace
cd /workspace/ros2_ws
colcon build --symlink-install
source install/setup.bash

# 4. terminal 1: realsense camera
ros2 launch realsense2_camera rs_launch.py \
  camera_namespace:=perception \
  camera_name:=table_cam

# 5. terminal 2: color detector
ros2 launch table_perception detection.launch.py

# 6. terminal 3: visualize (select /perception/debug_image)
ros2 run rqt_image_view rqt_image_view
```

to see the detections as text: `ros2 topic echo /perception/detections`.

to shut down: `docker compose -f docker-compose.dev.yml down`.

## topics and parameters

| parameter           | default                                 | description                     |
|---------------------|-----------------------------------------|---------------------------------|
| `input_topic`       | `/perception/table_cam/color/image_raw` | input image                     |
| `output_topic`      | `/perception/detections`                | detections (`Detection2DArray`) |
| `debug_image_topic` | `/perception/debug_image`               | image with bounding boxes drawn |

to use different topics, edit [detection.launch.py](ros2_ws/src/table_perception/launch/detection.launch.py) or use `ros2 run table_perception color_detector --ros-args -p input_topic:=/other/topic` (use absolute topic names, since the node runs without the `/perception` namespace).

the hsv ranges and the minimum contour area (500 px²) are hardcoded in [color_detector.py](ros2_ws/src/table_perception/table_perception/color_detector.py). each detection's `score` is the fraction of the image covered by the contour, not a statistical confidence.

the environment uses `ROS_DOMAIN_ID=42` and `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`; other machines that need to communicate with the container must use the same values.
