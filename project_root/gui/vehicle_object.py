from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsPolygonItem, QApplication, QPushButton, QVBoxLayout, QWidget, QGraphicsRectItem
from PySide6.QtGui import QPolygonF, QTransform, QPen, QBrush
from PySide6.QtCore import Qt, QPointF
import sys
import math
from gui.vehicle_config import VehicleConfigBase
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt

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