#!/usr/bin/env bash
set -euo pipefail
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=waffle
echo 'Starting TurtleBot3 Gazebo Classic. Keep this terminal open.'
exec ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
