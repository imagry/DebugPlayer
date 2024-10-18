from PySide6.QtWidgets import QGraphicsPolygonItem, QGraphicsRectItem
from PySide6.QtGui import QPolygonF, QPen, QBrush, QPainterPath, QTransform
from PySide6.QtCore import Qt, QPointF, QRectF
import math
import pyqtgraph as pg



class VehicleGraphicsItem(pg.GraphicsObject):
    def __init__(self, vehicle_config):
        super().__init__()
        self.vehicle_config = vehicle_config
        self.pose = (0, 0, 0)  # x, y, theta
        self.generate_vehicle_shape()

    def generate_vehicle_shape(self):
        """Generate the vehicle shape as a QPainterPath."""
        length = self.vehicle_config.vehicle_length_meters
        width = self.vehicle_config.vehicle_width_meters

        # Define the vehicle rectangle
        self.vehicle_path = QPainterPath()
        self.vehicle_path.moveTo(0, -width / 2)
        self.vehicle_path.lineTo(0, width / 2)
        self.vehicle_path.lineTo(length, width / 2)
        self.vehicle_path.lineTo(length, -width / 2)
        self.vehicle_path.closeSubpath()

    def set_pose(self, x, y, theta):
        """Set the vehicle's pose."""
        self.pose = (x, y, math.radians(theta))
        self.update()

    def paint(self, painter, option, widget):
        """Draw the vehicle."""
        x, y, theta = self.pose
        
        # Save the painter state
        painter.save()

        # Move to the vehicle's position and apply rotation
        transform = QTransform()
        transform.translate(x, y)
        transform.rotate(math.degrees(theta))
        painter.setTransform(transform)

        # Set brush and pen
        painter.setBrush(QBrush(Qt.lightGray))
        painter.setPen(QPen(Qt.black))

        # Draw the vehicle shape
        painter.drawPath(self.vehicle_path)

        # Restore the painter state
        painter.restore()

    def boundingRect(self):
        """Return the bounding rectangle of the vehicle."""
        length = self.vehicle_config.vehicle_length_meters
        width = self.vehicle_config.vehicle_width_meters
        return QRectF(0, -width / 2, length, width)


class VehicleObject(QGraphicsPolygonItem):
    """
    VehicleObject is a class that represents a vehicle in a graphical scene using QGraphicsPolygonItem.
    It initializes the vehicle's dimensions, state, and visual elements such as the vehicle body, bounding box, and wheels.

    Attributes:
        length (float): Length of the vehicle in meters.
        width (float): Width of the vehicle in meters.
        wheelbase (float): Distance between the front and rear axles in meters.
        front_axle_offset (float): Offset of the front axle from the front of the vehicle in meters.
        rear_axle_offset (float): Offset of the rear axle from the rear of the vehicle in meters.
        x (float): X-coordinate of the vehicle's position (rear end).
        y (float): Y-coordinate of the vehicle's position (rear end).
        theta (float): Heading of the vehicle in radians, positive counterclockwise.
        wheel_angle (float): Steering angle of the front wheels in radians.
        speed (float): Speed of the vehicle.
        acceleration (float): Acceleration of the vehicle.
        bounding_box (QGraphicsRectItem): Bounding box of the vehicle.
        front_left_wheel (QGraphicsPolygonItem): Front left wheel of the vehicle.
        front_right_wheel (QGraphicsPolygonItem): Front right wheel of the vehicle.
        rear_left_wheel (QGraphicsPolygonItem): Rear left wheel of the vehicle.
        rear_right_wheel (QGraphicsPolygonItem): Rear right wheel of the vehicle.

    Methods:
        __init__(config): Initializes the VehicleObject with the given configuration.
        _create_vehicle_body(): Creates the shape of the vehicle based on its length and width.
        _create_bounding_box(): Creates a bounding box for the vehicle.
        _create_wheels(): Creates the front and rear wheels of the vehicle.
        update_state(x, y, theta, wheel_angle, speed, acceleration): Updates the vehicle state properties.
        update_vehicle_position(): Updates the position and orientation of the vehicle body.
        update_wheel_positions(): Updates the positions of the front and rear wheels based on the steering angle.
        _update_wheel(wheel_item, position, angle): Updates a specific wheel's position and rotation.
        set_pose_at_front_axle(x, y, theta): Sets the vehicle pose such that the front axle is at (x, y, theta).
        get_pose_at_front_axle(): Gets the vehicle pose at the front axle.
        set_pose_at_rear_axle(x, y, theta): Sets the vehicle pose such that the rear axle is at (x, y, theta).
        get_pose_at_rear_axle(): Gets the vehicle pose at the rear axle.
        set_pose_at_vehicle_center(x, y, theta): Sets the vehicle pose such that the center is at (x, y, theta).
        get_pose_at_vehicle_center(): Gets the vehicle pose at the center.
        set_pose_at_custom_from_front_axle(x, y, theta, dx, dy): Sets the vehicle pose at a custom point from the front axle.
        get_pose_at_custom_from_front_axle(dx, dy): Gets the vehicle pose at a custom point from the front axle.
    """
    def __init__(self, config):
        super().__init__()
        self.length = config.vehicle_length_meters  # in meters
        self.width = config.vehicle_width_meters  # in meters
        self.wheelbase = config.vehicle_wheels_base  # in meters
        self.front_axle_offset = config.vehicle_fron_axle_offset  # in meters
        self.rear_axle_offset = self.length - self.wheelbase - self.front_axle_offset

        # Initialize vehicle state
        self.x = 0  # Position of the rear end
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
        """Update vehicle state properties.
        (self.x, self.y) always refers to the rear end of the vehicle 
        (the origin of the vehicle's local coordinate system)."""
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
        rear_axle_x = self.rear_axle_offset  # Rear axle position

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

    def set_pose_at_front_axle(self, x, y, theta):
        """Set the vehicle pose such that the front axle is at (x, y, theta)."""
        dx = self.length - self.front_axle_offset
        self.theta = theta
        self.x = x - dx * math.cos(theta)
        self.y = y - dx * math.sin(theta)
        self.update_vehicle_position()
        self.update_wheel_positions()

    def get_pose_at_front_axle(self):
        """Get the vehicle pose at the front axle."""
        dx = self.length - self.front_axle_offset
        x_front_axle = self.x + dx * math.cos(self.theta)
        y_front_axle = self.y + dx * math.sin(self.theta)
        return x_front_axle, y_front_axle, self.theta

    def set_pose_at_rear_axle(self, x, y, theta):
        """Set the vehicle pose such that the rear axle is at (x, y, theta)."""
        dx = self.rear_axle_offset
        self.theta = theta
        self.x = x - dx * math.cos(theta)
        self.y = y - dx * math.sin(theta)
        self.update_vehicle_position()
        self.update_wheel_positions()

    def get_pose_at_rear_axle(self):
        """Get the vehicle pose at the rear axle."""
        dx = self.rear_axle_offset
        x_rear_axle = self.x + dx * math.cos(self.theta)
        y_rear_axle = self.y + dx * math.sin(self.theta)
        return x_rear_axle, y_rear_axle, self.theta

    def set_pose_at_vehicle_center(self, x, y, theta):
        """Set the vehicle pose such that the vehicle center is at (x, y, theta)."""
        dx = self.length / 2
        self.theta = theta
        self.x = x - dx * math.cos(theta)
        self.y = y - dx * math.sin(theta)
        self.update_vehicle_position()
        self.update_wheel_positions()

    def get_pose_at_vehicle_center(self):
        """Get the vehicle pose at the vehicle center."""
        dx = self.length / 2
        x_center = self.x + dx * math.cos(self.theta)
        y_center = self.y + dx * math.sin(self.theta)
        return x_center, y_center, self.theta

    def set_pose_at_custom_from_front_axle(self, x, y, theta, dx, dy):
        """Set the vehicle pose at a custom point from the front axle.
        The custom point is at (dx, dy) from the front axle in the vehicle's local coordinate system.
        """
        # Displacement from rear end to front axle
        front_axle_x = self.length - self.front_axle_offset
        # Total displacement from rear end to custom point
        dx_total = front_axle_x + dx
        dy_total = dy
        # Compute global displacement
        global_dx = dx_total * math.cos(theta) - dy_total * math.sin(theta)
        global_dy = dx_total * math.sin(theta) + dy_total * math.cos(theta)
        self.theta = theta
        self.x = x - global_dx
        self.y = y - global_dy
        self.update_vehicle_position()
        self.update_wheel_positions()

    def get_pose_at_custom_from_front_axle(self, dx, dy):
        """Get the vehicle pose at a custom point from the front axle.
        The custom point is at (dx, dy) from the front axle in the vehicle's local coordinate system.
        """
        # Displacement from rear end to front axle
        front_axle_x = self.length - self.front_axle_offset
        # Total displacement from rear end to custom point
        dx_total = front_axle_x + dx
        dy_total = dy
        # Compute global displacement
        global_dx = dx_total * math.cos(self.theta) - dy_total * math.sin(self.theta)
        global_dy = dx_total * math.sin(self.theta) + dy_total * math.cos(self.theta)
        x_custom = self.x + global_dx
        y_custom = self.y + global_dy
        return x_custom, y_custom, self.theta
