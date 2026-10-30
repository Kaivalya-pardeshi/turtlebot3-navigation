#!/usr/bin/env bash
set -euo pipefail
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=waffle
MAP=/opt/ros/humble/share/turtlebot3_navigation2/map/map.yaml
if [[ ! -f "$MAP" ]]; then echo "Map missing: $MAP" >&2; exit 1; fi
echo 'Initialize pose in RViz using 2D Pose Estimate after launch.'
exec ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:="$MAP"
