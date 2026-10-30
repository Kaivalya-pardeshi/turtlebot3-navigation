from setuptools import find_packages, setup

package_name = 'tb3_nav_tools'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Student Developer',
    maintainer_email='maintainer@example.com',
    description='Small diagnostics and navigation goal logger for TurtleBot3 Nav2 demos',
    license='MIT',
    entry_points={'console_scripts': [
        'health_check = tb3_nav_tools.health_check:main',
        'send_goal = tb3_nav_tools.send_goal:main',
    ]},
)
