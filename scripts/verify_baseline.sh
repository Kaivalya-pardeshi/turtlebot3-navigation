#!/usr/bin/env bash
set -euo pipefail
source /opt/ros/humble/setup.bash
printf 'ROS: %s\n' "${ROS_DISTRO:-unset}"
printf '\nPackages:\n'
for pkg in turtlebot3_gazebo turtlebot3_navigation2 nav2_bt_navigator tb3_nav_tools; do
  ros2 pkg prefix "$pkg" || true
done
printf '\nTopics:\n'
ros2 topic list
printf '\nActions:\n'
ros2 action list
printf '\nAMCL state:\n'
ros2 lifecycle get /amcl || true
printf '\nBT navigator state:\n'
ros2 lifecycle get /bt_navigator || true
