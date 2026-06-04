ARG ROS_DISTRO=jazzy
FROM osrf/ros:${ROS_DISTRO}-desktop

ARG ROS_DISTRO
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
      git-lfs \
      wget \
      curl \
      nano \
      build-essential \
      python3-colcon-common-extensions \
      python3-rosdep \
      ros-${ROS_DISTRO}-ros-gz \
      ros-${ROS_DISTRO}-ros-gz-sim \
      ros-${ROS_DISTRO}-ros-gz-bridge \
 && rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /root/.bashrc \
 && echo "[ -f /root/ros2_ws/install/setup.bash ] && source /root/ros2_ws/install/setup.bash" >> /root/.bashrc

WORKDIR /root/ros2_ws

CMD ["bash"]
