# TurtleBot3 Reliable Navigation — ROS 2 Humble

Student robotics integration project for an indoor obstacle-navigation assignment. Runs a **TurtleBot3 Waffle** in **Gazebo Classic 11** and uses the existing **Navigation2 (Nav2)** stack (AMCL, map server, planners, controllers, behavior tree navigator). This repository adds **read-only health checks** and an **optional action-goal CSV logger**; it does **not** implement a custom planner.

> **Status:** ROS 2 Humble and Gazebo/TurtleBot3 integration were demonstrated during setup; the final autonomous NavigateToPose success remains **to be verified on the target computer**. No successful navigation trial is claimed by this repository.

## Prerequisites
- Windows 11 + **WSL 2 Ubuntu 22.04**, or native Ubuntu 22.04
- ROS 2 Humble (`ros-humble-desktop`)
- Gazebo Classic 11, `ros-humble-gazebo-ros-pkgs`
- `ros-humble-turtlebot3`, `ros-humble-turtlebot3-simulations`, `ros-humble-navigation2`, `ros-humble-nav2-bringup`
- `ros-humble-turtlebot3-navigation2` (normally installed with TurtleBot3/Nav2 packages)
- `python3-colcon-common-extensions`, `ros-humble-tf-transformations`

Install on correctly configured Ubuntu 22.04/Humble:

```bash
sudo apt update
sudo apt install -y ros-humble-desktop gazebo ros-humble-gazebo-ros-pkgs \
  ros-humble-turtlebot3 ros-humble-turtlebot3-simulations \
  ros-humble-turtlebot3-navigation2 ros-humble-navigation2 \
  ros-humble-nav2-bringup ros-humble-tf-transformations \
  python3-colcon-common-extensions
```

## Build custom diagnostic package

Clone this repository inside the Ubuntu Linux filesystem (for example `~/projects`), **not** `/mnt/c` for improved WSL build performance.

```bash
cd ~/projects/turtlebot3-reliable-navigation
source /opt/ros/humble/setup.bash
colcon build --base-paths src --symlink-install
source install/setup.bash
```

## Run

Open two **Ubuntu 22.04** terminals. Do not accidentally enter Ubuntu 26.04 or PowerShell for ROS commands.

**Terminal 1 — Gazebo**
```bash
cd ~/projects/turtlebot3-reliable-navigation
./scripts/start_sim.sh
```
Check that `waffle` actually spawned and that `ros2 topic echo /scan --once` and `ros2 topic echo /odom --once` work. On slower WSL systems, the first Gazebo startup may exceed the default spawn-service timeout. If `/spawn_entity` eventually appears but the robot is absent, see troubleshooting.

**Terminal 2 — Navigation + RViz**
```bash
cd ~/projects/turtlebot3-reliable-navigation
./scripts/start_nav.sh
```

1. In RViz, keep the fixed frame `map`. Verify that the occupancy map visually matches the Gazebo world.
2. Click **2D Pose Estimate** and click-drag from the robot's *actual* map location in its facing direction. Repeat until the laser scan matches the obstacles. A connected TF does not alone prove localization accuracy.
3. Check both lifecycle nodes: `ros2 lifecycle get /amcl` and `ros2 lifecycle get /bt_navigator` (both should report `active [3]`).
4. Click **Nav2 Goal** in an open white region; drag to set heading. Observe planned path, motion, and final status. Do not choose a goal inside an obstacle or inflated region.

**Terminal 3 — Diagnostics**
```bash
source /opt/ros/humble/setup.bash
cd ~/projects/turtlebot3-reliable-navigation
source install/setup.bash
ros2 run tb3_nav_tools health_check
./scripts/verify_baseline.sh
```

**Optional CLI navigation goal and logging** (ONLY after initial pose is correctly set and target coordinates are known to be collision-free):
```bash
ros2 run tb3_nav_tools send_goal --x 0.5 --y 0.5 --yaw 0 --timeout 120
```
This example coordinate is **illustrative**; choose a valid free-space destination on your map first. Result CSV is written to `~/tb3_nav_results.csv`. It records goal status and elapsed **wall-clock** duration, not distance error or obstacle clearance.

## Architecture

```text
Gazebo (physics + simulated LiDAR + odometry)
  | /scan, /odom, /tf, /clock
  v
AMCL + static occupancy map -> map->odom TF
  |
  v
Nav2 Planner + Costmaps -> Controller -> /cmd_vel -> Gazebo robot
  ^
  | NavigateToPose ROS 2 action
RViz Nav2 Goal  /  optional goal_logger

health_check observes ROS topics, action availability, and map->base_link TF.
```

## Evidence and limitations

- Demonstration: add a genuine 1–2 minute video link to `docs/demo.md` after recording.
- Trial results: fill in `docs/experiments.md` using actual observations.
- Source of navigation stack and models: official [ROBOTIS TurtleBot3](https://emanual.robotis.com/docs/en/platform/turtlebot3/nav_simulation/) and [Nav2](https://navigation.ros.org/). They are installed dependencies, not original implementations.
- Gazebo Classic is end-of-life; it is used here specifically for the Humble-compatible assignment setup.
- WSL graphics performance varies; `glxinfo -B` can help identify GPU acceleration.

## Troubleshooting

| Symptom | Check / remedy |
|---|---|
| `/spawn_entity` unavailable | Check `ros2 service list`, `pgrep -a gzserver`; allow world to initialize. Do not spawn duplicates. |
| Robot missing, world visible | `ros2 service list`; inspect Gazebo Models list; spawn once via `gazebo_ros spawn_entity.py` only if missing. |
| `Invalid frame ID map` | Verify AMCL active and use RViz **2D Pose Estimate**. Check `ros2 run tf2_ros tf2_echo map base_link`. |
| RViz messy or plugin panel missing | Temporarily hide costmap, particle, and laser layers; check Nav2 directly with lifecycle/action CLI. |
| Robot fails to move | Confirm `ros2 action info /navigate_to_pose`, `/cmd_vel`, costmaps, and goal acceptance. |
| WSL wrong Ubuntu version | In Windows PowerShell use `wsl -d Ubuntu-22.04`. |

## License
MIT — see `LICENSE`. Author metadata and submission evidence must be updated before publishing.
