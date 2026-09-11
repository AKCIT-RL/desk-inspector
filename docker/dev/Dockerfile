FROM osrf/ros:humble-desktop

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl gnupg2 \
    && mkdir -p /etc/apt/keyrings \
    && curl -sSf https://librealsense.realsenseai.com/Debian/librealsenseai.asc | gpg --dearmor -o /etc/apt/keyrings/librealsense.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/librealsense.gpg] https://librealsense.realsenseai.com/Debian/apt-repo $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/librealsense.list \
    && apt-get update && apt-get install -y \
    librealsense2-utils \
    librealsense2-dev \
    ros-humble-realsense2-camera \
    ros-humble-realsense2-camera-msgs \
    ros-humble-cv-bridge \
    ros-humble-vision-msgs \
    ros-humble-rqt-image-view \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-foxglove-bridge \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir opencv-python-headless "numpy<2"

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
WORKDIR /workspace/ros2_ws

RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc
RUN echo "if [ -f /workspace/ros2_ws/install/setup.bash ]; then source /workspace/ros2_ws/install/setup.bash; fi" >> /root/.bashrc

CMD ["/bin/bash"]
