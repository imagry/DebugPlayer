from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsPolygonItem, QApplication, QPushButton, QVBoxLayout, QWidget, QGraphicsRectItem
from PySide6.QtGui import QPolygonF, QTransform, QPen, QBrush
from PySide6.QtCore import Qt, QPointF
import sys
import math

from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zoom_factor = 1.15  # Zoom factor for each step

    def wheelEvent(self, event):
        # Check the angle delta (wheel scroll amount)
        if event.angleDelta().y() > 0:
            self.scale(self.zoom_factor, self.zoom_factor)  # Zoom in
        else:
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)  # Zoom out
            

# VehicleConfigBase and configuration for niro_ev2 (already defined by you)
class VehicleConfigBase():
    def __init__(self, vehicle_name=None,
                 vehicle_type=None,
                 vehicle_model=None,
                 vehicle_year=None,
                 vehicle_width_meters=None,
                 vehicle_length_meters=None,
                 vehicle_wheels_base=None,
                 vehicle_fron_axle_offset=None,
                 vehicle_center_of_gravity_offset_from_front_axle=None,
                 steering_ratio=None):
        self.vehicle_name = vehicle_name
        self.vehicle_type = vehicle_type
        self.vehicle_model = vehicle_model
        self.vehicle_year = vehicle_year
        self.vehicle_width_meters = vehicle_width_meters
        self.vehicle_length_meters = vehicle_length_meters
        self.vehicle_wheels_base = vehicle_wheels_base
        self.vehicle_fron_axle_offset = vehicle_fron_axle_offset
        self.vehicle_center_of_gravity_offset_from_front_axle = vehicle_center_of_gravity_offset_from_front_axle
        self.steering_ratio = steering_ratio


niro_ev2 = VehicleConfigBase(
    vehicle_name='niro_ev2',
    vehicle_width_meters=1.825,
    vehicle_length_meters=4.420,
    vehicle_wheels_base=2.720,
    vehicle_fron_axle_offset=0.895,
    steering_ratio=13.3
)


class VehicleObject(QGraphicsPolygonItem):
    def __init__(self, config):
        super().__init__()
        self.length = config.vehicle_length_meters  # in meters
        self.width = config.vehicle_width_meters  # in meters
        self.wheelbase = config.vehicle_wheels_base  # in meters
        self.front_axle_offset = config.vehicle_fron_axle_offset  # in meters
        self.rear_axle_offset = self.length - self.wheelbase - self.front_axle_offset

        # Initialize vehicle state
        self.x = 0
        self.y = 0
        self.theta = 0  # Heading in radians, positive counterclockwise
        self.wheel_angle = 0  # Steering angle of front wheels
        self.speed = 0
        self.acceleration = 0

        # Create visual elements
        self._create_vehicle_body()
        self._create_bounding_box()
        self._create_wheels()

    def _create_vehicle_body(self):
        """Create the shape of the vehicle based on its length and width."""
        vehicle_shape = QPolygonF([
            QPointF(0, -self.width / 2),              # Rear-left corner
            QPointF(0, self.width / 2),               # Rear-right corner
            QPointF(self.length, self.width / 2),     # Front-right corner
            QPointF(self.length, -self.width / 2),    # Front-left corner
        ])
        self.setPolygon(vehicle_shape)
        self.setBrush(QBrush(Qt.lightGray))

    def _create_bounding_box(self):
        """Create a bounding box for the vehicle."""
        self.bounding_box = QGraphicsRectItem(0, -self.width / 2, self.length, self.width)
        pen_green = QPen(Qt.green, 1.0)
        self.bounding_box.setPen(pen_green)
        self.bounding_box.setBrush(Qt.NoBrush)
        self.bounding_box.setParentItem(self)  # Make bounding box a child of the vehicle

    def _create_wheels(self):
        """Create the front and rear wheels."""
        wheel_width = self.width * 0.025  # Adjust width as needed
        wheel_length = self.length * 0.3  # Adjust length as needed

        # Define the rectangular shape for the wheels along x-axis
        wheel_shape = QPolygonF([
            QPointF(-wheel_length / 2, -wheel_width / 2),
            QPointF(wheel_length / 2, -wheel_width / 2),
            QPointF(wheel_length / 2, wheel_width / 2),
            QPointF(-wheel_length / 2, wheel_width / 2)
        ])

        # Create wheels as child items of the vehicle
        self.front_left_wheel = QGraphicsPolygonItem(wheel_shape, self)
        self.front_left_wheel.setBrush(QBrush(Qt.darkGray))
        self.front_left_wheel.setTransformOriginPoint(0, 0)

        self.front_right_wheel = QGraphicsPolygonItem(wheel_shape, self)
        self.front_right_wheel.setBrush(QBrush(Qt.darkGray))
        self.front_right_wheel.setTransformOriginPoint(0, 0)

        self.rear_left_wheel = QGraphicsPolygonItem(wheel_shape, self)
        self.rear_left_wheel.setBrush(QBrush(Qt.darkGray))
        self.rear_left_wheel.setTransformOriginPoint(0, 0)

        self.rear_right_wheel = QGraphicsPolygonItem(wheel_shape, self)
        self.rear_right_wheel.setBrush(QBrush(Qt.darkGray))
        self.rear_right_wheel.setTransformOriginPoint(0, 0)

    def update_state(self, x, y, theta, wheel_angle, speed, acceleration):
        """Update vehicle state properties."""
        self.x = x
        self.y = y
        self.theta = theta
        self.wheel_angle = wheel_angle
        self.speed = speed
        self.acceleration = acceleration
        self.update_vehicle_position()
        self.update_wheel_positions()

    def update_vehicle_position(self):
        """Update the position and orientation of the vehicle body."""
        self.setPos(self.x, self.y)
        self.setRotation(math.degrees(self.theta))

    def update_wheel_positions(self):
        """Update the positions of the front and rear wheels based on the steering angle."""
        front_axle_x = self.length - self.front_axle_offset  # Front axle near the front of the vehicle
        rear_axle_x = self.rear_axle_offset  # Rear axle at the back of the vehicle

        left_y = -self.width / 2
        right_y = self.width / 2

        # Set front wheels (with rotation based on steering)
        left_front_pos = QPointF(front_axle_x, left_y)
        right_front_pos = QPointF(front_axle_x, right_y)

        self._update_wheel(self.front_left_wheel, left_front_pos, self.wheel_angle)
        self._update_wheel(self.front_right_wheel, right_front_pos, self.wheel_angle)

        # Set rear wheels (no steering angle)
        left_rear_pos = QPointF(rear_axle_x, left_y)
        right_rear_pos = QPointF(rear_axle_x, right_y)
        self._update_wheel(self.rear_left_wheel, left_rear_pos, 0)
        self._update_wheel(self.rear_right_wheel, right_rear_pos, 0)

    def _update_wheel(self, wheel_item, position, angle):
        """Update a specific wheel's position and rotation."""
        wheel_item.setPos(position)
        wheel_item.setRotation(math.degrees(angle))


def setup_scene():
    """
    Setup the QGraphicsScene and view with axes and grid for visualization.
    """
    scene = QGraphicsScene()

    # Replace QGraphicsView with ZoomableGraphicsView
    view = ZoomableGraphicsView(scene)
    view.setGeometry(100, 100, 600, 600)
    view.scale(5, 5)

    scene.setSceneRect(-50, -50, 100, 100)

    # Add grid and axes
    grid_size = 10
    pen_gray = QPen(Qt.gray, 0.05)
    pen_red = QPen(Qt.red, 0.1)
    pen_blue = QPen(Qt.blue, 0.1)

    for x in range(-50, 51, grid_size):
        scene.addLine(x, -50, x, 50, pen_gray)  # Vertical grid lines
    for y in range(-50, 51, grid_size):
        scene.addLine(-50, y, 50, y, pen_gray)  # Horizontal grid lines

    scene.addLine(-50, 0, 50, 0, pen_red)  # X-axis in red
    scene.addLine(0, -50, 0, 50, pen_blue)  # Y-axis in blue

    return scene, view


def main():
    app = QApplication(sys.argv)

    # Setup scene and view
    scene, view = setup_scene()

    # Create vehicle instance using niro_ev2 config
    vehicle = VehicleObject(config=niro_ev2)
    vehicle.update_state(x=0, y=0, theta=math.radians(45), wheel_angle=math.radians(-45), speed=5, acceleration=0.1)

    # Add vehicle components to the scene
    scene.addItem(vehicle)  # Add the vehicle's body

    # Control panel to update vehicle state
    def move_vehicle():
        # Get the current state
        x = vehicle.x
        y = vehicle.y
        theta = vehicle.theta  # Current heading in radians
        wheel_angle = vehicle.wheel_angle  # Steering angle of front wheels
        speed = vehicle.speed
        dt = 0.1  # Time step (could be modified)

        # Bicycle model parameters
        L = vehicle.wheelbase  # Vehicle's wheelbase

        # Compute the rate of change of heading (theta) based on the steering angle and speed
        if abs(wheel_angle) > 1e-3:  # Avoid division by zero in low steering angles
            radius_of_curvature = L / math.tan(wheel_angle)  # Turning radius
            dtheta = speed * dt / radius_of_curvature  # Change in heading
        else:
            dtheta = 0  # No change in heading if there's no steering angle

        # Update the vehicle's position (x, y) and heading (theta)
        new_theta = theta + dtheta
        new_x = x + speed * math.cos(theta) * dt
        new_y = y + speed * math.sin(theta) * dt

        # Update the vehicle state
        vehicle.update_state(new_x, new_y, new_theta, wheel_angle, speed, vehicle.acceleration)

    # Setup control widget to move the vehicle
    control_widget = QWidget()
    layout = QVBoxLayout()
    move_button = QPushButton("Move Vehicle")
    move_button.clicked.connect(move_vehicle)
    layout.addWidget(move_button)
    control_widget.setLayout(layout)
    control_widget.setGeometry(920, 100, 200, 100)
    control_widget.show()

    # Show the view and start the application
    view.show()
    sys.exit(app.exec())


import unittest
from PySide6.QtCore import QPointF
import math

class TestVehicleObject(unittest.TestCase):
    def setUp(self):
        self.vehicle_config = VehicleConfigBase(
            vehicle_name='test_vehicle',
            vehicle_width_meters=2.0,
            vehicle_length_meters=4.5,
            vehicle_wheels_base=3.0,
            vehicle_fron_axle_offset=0.5
        )
        self.vehicle = VehicleObject(self.vehicle_config)

    def test_initial_position(self):
        """Test that the vehicle starts at (0, 0) with no rotation."""
        self.assertEqual(self.vehicle.x, 0)
        self.assertEqual(self.vehicle.y, 0)
        self.assertEqual(self.vehicle.theta, 0)

    def test_wheel_positioning(self):
        """Test that the wheels are positioned correctly relative to the vehicle."""
        self.vehicle.update_wheel_positions()

        # Check that the front wheels are placed correctly
        front_axle_x = self.vehicle.length - self.vehicle.front_axle_offset
        rear_axle_x = 0
        left_y = -self.vehicle.width / 2
        right_y = self.vehicle.width / 2

        self.assertEqual(self.vehicle.front_left_wheel.pos(), QPointF(front_axle_x, left_y))
        self.assertEqual(self.vehicle.front_right_wheel.pos(), QPointF(front_axle_x, right_y))

    def test_wheel_steering_angle(self):
        """Test that the front wheels rotate correctly based on the steering angle."""
        self.vehicle.update_state(0, 0, 0, math.radians(45), 0, 0)
        front_wheel_angle = math.degrees(self.vehicle.wheel_angle)

        # Verify the wheel angle is applied correctly
        front_left_transform = self.vehicle.front_left_wheel.transform()
        front_right_transform = self.vehicle.front_right_wheel.transform()
        self.assertAlmostEqual(front_left_transform.m11(), math.cos(math.radians(45)), places=2)
        self.assertAlmostEqual(front_right_transform.m11(), math.cos(math.radians(45)), places=2)

    def test_vehicle_movement(self):
        """Test vehicle movement when updating position."""
        self.vehicle.update_state(5, 5, math.radians(45), math.radians(0), 5, 0.1)
        self.assertEqual(self.vehicle.x, 5)
        self.assertEqual(self.vehicle.y, 5)
        self.assertAlmostEqual(self.vehicle.theta, math.radians(45))

# if __name__ == '__main__':
#     unittest.main()


if __name__ == "__main__":
    main()
