"""One-goal Nav2 action client with CSV outcome logging."""
import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from action_msgs.msg import GoalStatus
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler


class GoalRunner(Node):
    def __init__(self):
        super().__init__('tb3_goal_logger')
        self.declare_parameter('use_sim_time', True)
        self.client = ActionClient(self, NavigateToPose, '/navigate_to_pose')

    def execute(self, x, y, yaw, timeout):
        if not self.client.wait_for_server(timeout_sec=10.0):
            raise RuntimeError('Nav2 NavigateToPose action unavailable')
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        q = quaternion_from_euler(0, 0, yaw)
        pose.pose.orientation.x, pose.pose.orientation.y, pose.pose.orientation.z, pose.pose.orientation.w = map(float, q)
        goal = NavigateToPose.Goal()
        goal.pose = pose
        sent = self.client.send_goal_async(goal, feedback_callback=self.feedback)
        rclpy.spin_until_future_complete(self, sent, timeout_sec=15.0)
        if not sent.done():
            raise RuntimeError('Goal acceptance timed out')
        handle = sent.result()
        if not handle.accepted:
            return 'REJECTED'
        self.get_logger().info('Goal accepted')
        result_future = handle.get_result_async()
        deadline = time.monotonic() + timeout
        while rclpy.ok() and not result_future.done() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.2)
        if not result_future.done():
            self.get_logger().warning('Timeout: requesting goal cancellation')
            cancel = handle.cancel_goal_async()
            rclpy.spin_until_future_complete(self, cancel, timeout_sec=5.0)
            return 'TIMEOUT_CANCEL_REQUESTED'
        status = result_future.result().status
        return {GoalStatus.STATUS_SUCCEEDED:'SUCCEEDED', GoalStatus.STATUS_ABORTED:'ABORTED',
                GoalStatus.STATUS_CANCELED:'CANCELED'}.get(status, f'STATUS_{status}')

    def feedback(self, message):
        fb = message.feedback
        self.get_logger().info(f'distance_remaining={fb.distance_remaining:.2f} m')


def append_csv(filename, row):
    path = Path(filename).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open('a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not exists:
            writer.writerow(['timestamp_utc', 'x_m', 'y_m', 'yaw_rad', 'status', 'elapsed_wall_sec'])
        writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description='Send map-frame Nav2 goal and log result')
    parser.add_argument('--x', type=float, required=True)
    parser.add_argument('--y', type=float, required=True)
    parser.add_argument('--yaw', type=float, default=0.0, help='heading in radians')
    parser.add_argument('--timeout', type=float, default=120.0)
    parser.add_argument('--csv', default='~/tb3_nav_results.csv')
    args = parser.parse_args()
    rclpy.init()
    node = GoalRunner()
    began = time.monotonic()
    status = 'ERROR'
    try:
        status = node.execute(args.x, args.y, args.yaw, args.timeout)
    except Exception as exc:
        node.get_logger().error(str(exc))
    finally:
        elapsed = round(time.monotonic() - began, 2)
        append_csv(args.csv, [datetime.now(timezone.utc).isoformat(), args.x, args.y, args.yaw, status, elapsed])
        print(f'Goal result: {status}; elapsed wall time: {elapsed}s')
        node.destroy_node()
        rclpy.shutdown()
    if status != 'SUCCEEDED':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
