import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
from cv_bridge import CvBridge
import cv2
import numpy as np


class ColorCubeDetector(Node):
    def __init__(self):
        super().__init__('color_cube_detector')

        self.bridge = CvBridge()

        self.color_ranges = {
            'red': [
                (np.array([0, 120, 70]), np.array([8, 255, 255])),
                (np.array([170, 120, 70]), np.array([179, 255, 255])),
            ],
            'yellow': [
                (np.array([20, 100, 100]), np.array([35, 255, 255])),
            ],
            'green': [
                (np.array([40, 70, 70]), np.array([85, 255, 255])),
            ],
            'purple': [
                (np.array([125, 60, 60]), np.array([155, 255, 255])),
            ],
        }

        self.draw_colors = {
            'red': (0, 0, 255),
            'yellow': (0, 255, 255),
            'green': (0, 255, 0),
            'purple': (255, 0, 255),
        }

        self.min_contour_area = 500

        self.declare_parameter('input_topic', '/perception/table_cam/color/image_raw')
        self.declare_parameter('output_topic', '/perception/detections')
        self.declare_parameter('debug_image_topic', '/perception/debug_image')

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value
        debug_topic = self.get_parameter('debug_image_topic').value

        self.sub = self.create_subscription(Image, input_topic, self.image_callback, 10)
        self.det_pub = self.create_publisher(Detection2DArray, output_topic, 10)
        self.debug_pub = self.create_publisher(Image, debug_topic, 10)

        self.get_logger().info(f'Ouvindo {input_topic}, publicando deteccoes em {output_topic}')

    def image_callback(self, msg: Image):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        detections = Detection2DArray()
        detections.header = msg.header

        debug = frame.copy()

        for color_name, ranges in self.color_ranges.items():
            mask = None
            for lo, hi in ranges:
                m = cv2.inRange(hsv, lo, hi)
                mask = m if mask is None else cv2.bitwise_or(mask, m)

            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < self.min_contour_area:
                    continue

                x, y, w, h = cv2.boundingRect(cnt)
                cx = x + w / 2.0
                cy = y + h / 2.0

                det = Detection2D()
                det.header = msg.header
                det.bbox.center.position.x = cx
                det.bbox.center.position.y = cy
                det.bbox.center.theta = 0.0
                det.bbox.size_x = float(w)
                det.bbox.size_y = float(h)

                hyp = ObjectHypothesisWithPose()
                hyp.hypothesis.class_id = color_name
                hyp.hypothesis.score = min(1.0, area / (frame.shape[0] * frame.shape[1]))
                det.results.append(hyp)

                detections.detections.append(det)

                draw_color = self.draw_colors.get(color_name, (255, 255, 255))
                cv2.rectangle(debug, (x, y), (x + w, y + h), draw_color, 2)
                cv2.putText(debug, color_name, (x, max(0, y - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, draw_color, 2)

        self.det_pub.publish(detections)

        debug_msg = self.bridge.cv2_to_imgmsg(debug, encoding='bgr8')
        debug_msg.header = msg.header
        self.debug_pub.publish(debug_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ColorCubeDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
