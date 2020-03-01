import pyrealsense2 as rs
import numpy as np
import cv2

p = 1
print(p)
p = "t"
print(p)
while True:
    pass
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 90)
# config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)
# config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 90)
# config.enable_stream(rs.stream.infrared, 2, 640, 480, rs.format.y8, 30)
# config.enable_all_streams()
# Start streaming
pipeline.start(config)

try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        n = 1
        for fr in frames:
            f = np.asanyarray(fr.get_data())
            if n == 1:
                ff = cv2.applyColorMap(cv2.convertScaleAbs(f, alpha=0.03), cv2.COLORMAP_BONE)
                cv2.imshow(str(n), ff)
                n += 1
                continue
            cv2.imshow(str(n), f)
            n += 1
        cv2.waitKey(1)
        continue

        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Stack both images horizontally
        images = np.hstack((color_image, depth_colormap))

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)
        cv2.waitKey(1)

finally:

    # Stop streaming
    pipeline.stop()
