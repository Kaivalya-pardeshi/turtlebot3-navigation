# Submission form drafts — edit based on real evidence

## Approach
I used ROS 2 Humble with TurtleBot3 Waffle in Gazebo Classic and integrated the standard Nav2 stack. The map server provides a known occupancy map, AMCL estimates the robot's pose, and Nav2's existing planners, controller, costmaps, and NavigateToPose action handle goal-directed navigation. I wrote small diagnostics to check the system's ROS interfaces and an optional action client that logs goal results. I did not create a custom navigation algorithm.

## Challenges (confirmed during setup)
1. The first Gazebo world startup took longer than the robot spawn timeout. I checked the `/spawn_entity` service and Gazebo server/client processes, then manually spawned the robot once the service became available.
2. The `map` transform was initially missing because localization had not received a valid initial pose. I inspected AMCL warnings, used RViz's 2D Pose Estimate and checked TF connectivity.
3. Under WSL, I needed Ubuntu 22.04 specifically for ROS 2 Humble. I verified the Linux distribution and GPU-backed graphics before launching Gazebo.

## Learnings
ROS 2 topic communication, lifecycle states, TF connectivity, AMCL localization, sensor-backed costmaps, and the long-running NavigateToPose action all need to work together. A visible occupancy map alone is not proof of accurate localization; real simulation and action-result testing are essential.

**Before submitting:** replace any statement not backed by a screenshot or a verified test, and add the real navigation result.
