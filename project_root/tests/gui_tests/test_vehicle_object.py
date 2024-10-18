import sys
import math
import unittest
import math
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QApplication, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen
from PySide6.QtCore import QPointF
from gui.vehicle_config import niro_ev2
from gui.vehicle_config import VehicleConfigBase
from gui.vehicle_object import VehicleObject

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
