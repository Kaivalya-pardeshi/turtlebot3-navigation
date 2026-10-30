"""Read-only diagnostic for a TurtleBot3 simulation and its Nav2 server."""
import argparse
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from tf2_ros import Buffer, TransformListener


class HealthCheck(Node):
    def __init__(self):
        super().__init__('tb3_health_check')
        self.declare_parameter('use_sim_time', True)
        self.buffer = Buffer()
        self.tf_listener = TransformListener(self.buffer, self)
        self.action = ActionClient(self, NavigateToPose, '/navigate_to_pose')

    def check(self, seconds=8.0):
        deadline = time.monotonic() + seconds
        required_topics = ['/clock', '/scan', '/odom', '/map']
        observed = set()
        tf_ready = False
        action_ready = False
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.2)
            observed = {name for name, _ in self.get_topic_names_and_types()}
            try:
                tf_ready = self.buffer.can_transform('map', 'base_link', rclpy.time.Time())
            except Exception:
                tf_ready = False
            action_ready = self.action.server_is_ready()
            if all(t in observed for t in required_topics) and tf_ready and action_ready:
                break
        failures = []
        for topic in required_topics:
            good = topic in observed
            print(f'{"PASS" if good else "FAIL"} topic {topic}')
            if not good:
                failures.append(topic)
        print(f'{"PASS" if tf_ready else "FAIL"} transform map -> base_link')
        print(f'{"PASS" if action_ready else "FAIL"} action /navigate_to_pose')
        if not tf_ready:
            failures.append('map->base_link TF (check AMCL pose)')
        if not action_ready:
            failures.append('Nav2 action server')
        if failures:
            print('Unready components: ' + ', '.join(failures))
            return 1
        print('Health check passed (availability only; not a navigation test).')
        return 0


def main():
    parser = argparse.ArgumentParser(description='Read-only TurtleBot3/Navigation2 health check')
    parser.add_argument('--timeout', type=float, default=8.0)
    args = parser.parse_args()
    rclpy.init()
    node = HealthCheck()
    try:
        code = node.check(max(1.0, args.timeout))
    finally:
        node.destroy_node()
        rclpy.shutdown()
    if code:
        raise SystemExit(code)


if __name__ == '__main__':
    main()
