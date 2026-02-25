import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class CameraPublisher(Node):

    def __init__(self):
        super().__init__('usb_camera_publisher')

        self.declare_parameter('camera_id', 0)
        self.camera_id = self.get_parameter('camera_id').value

        self.topic_name = '/usb_camera/image_raw'

        self.publisher_ = self.create_publisher(
            Image,
            self.topic_name,
            10
        )

        self.get_frame_timer = self.create_timer(
            0.1,
            self.get_image_frame
        )

        self.image_elaboration_timer = self.create_timer(
            0.1,
            self.image_elaboration
        )

        self.bridge = CvBridge()
        self.frame = None
        self.img_ready = False

        self.cap = cv2.VideoCapture(self.camera_id)

        if not self.cap.isOpened():
            self.get_logger().error(
                f"Could not open video device with ID {self.camera_id}"
            )
            raise SystemExit

        self.get_logger().info(f"Camera {self.camera_id} started successfully")


    def get_image_frame(self):
        ret, frame = self.cap.read()

        if ret:
            self.frame = frame
            self.img_ready = True

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow('frame', gray)
            cv2.waitKey(1)


    def image_elaboration(self):
        if not self.img_ready:
            return

        frame = self.frame.copy()

        height, width = frame.shape[:2]

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        font_color = (255, 255, 255)
        font_thickness = 2

        resolution_text = f"Resolution: {width}x{height}"

        cv2.putText(frame, f"Device: {self.camera_id}", (10, 30),
                    font, font_scale, font_color, font_thickness)

        cv2.putText(frame, f"Topic: {self.topic_name}", (10, 60),
                    font, font_scale, font_color, font_thickness)

        cv2.putText(frame, resolution_text, (10, 90),
                    font, font_scale, font_color, font_thickness)

        image_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        self.publisher_.publish(image_msg)


def main(args=None):
    rclpy.init(args=args)
    node = CameraPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()