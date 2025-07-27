"""
ship_detector.py

A utility for detecting “ship” centers in all images of a given scene folder.

This module provides the ShipDetector class, which can run either:
  - “auto” detection: simple threshold + contour-based centroid finding, or
  - “manual” detection: GUI point-and-click to mark exactly two centers per image.

Usage:
    detector = ShipDetector("/path/to/scene_folder")
    detector.process_scene(action="auto")    # or action="manual"
    centers = detector.get_centers() - is a dict { filename: [(x1, y1), (x2, y2), …], … }
"""
import os
import cv2
import numpy as np

class ShipDetector:
    """
   Detects object centers (e.g., ships) in every image of a scene directory.

   Attributes:
       scene_path (str):
           Path to a folder containing image files (.jpg, .jpeg, .png).
       centers_per_image (dict[str, list[tuple[int, int]]]):
           Maps each image filename to the list of detected center coordinates.
   """
    def __init__(self, scene_path):
        """
       Initialize the detector for a single scene.

       Args:
           scene_path: Path to the directory with the images to process.
       """
        self.scene_path = scene_path
        self.centers_per_image = {}  # key: filename, value: list of centers (x, y)

    def process_scene(self,action):
        """
       Process every image in the scene, storing detected centers.

       Args:
           action: One of
               - "auto":   run automatic contour-based detection
               - "manual": run manual point-and-click detection

       Raises:
           ValueError: If `action` is not "auto" or "manual".
       """
        image_files = sorted(f for f in os.listdir(self.scene_path) if f.lower().endswith((".jpg", ".jpeg", ".png")))

        for fname in image_files:
            img_path = os.path.join(self.scene_path, fname)
            img = cv2.imread(img_path)
            if img is None:
                continue
            if action == "auto":
                self.centers_per_image[fname] = self._auto_detect_objects(img)
            elif action == "manual":
                self.centers_per_image[fname] = self._manual_detect_objects(img, fname)
            else:
                raise ValueError("Invalid action")



    def _manual_detect_objects(self, img, fname):
        """
       Let the user click exactly two points on the image to mark object centers.

       Opens a window showing `img`. The user left-clicks twice to select centers.

       Args:
           img:   The image in which to select points.
           fname: Filename (used in print statements).

       Returns:
           A list of up to two (x, y) tuples. If fewer than two points are selected,
           returns an empty list after warning.
       """
        centers = []
        def select_point(event, x, y, flags, param):
            # helper
            if event == cv2.EVENT_LBUTTONDOWN and len(centers) < 2:
                centers.append((x, y))
                print(f"Selected point {len(centers)} for {fname}: ({x}, {y})")
                cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
                cv2.imshow("Select centers", img)

        clone = img.copy()
        cv2.namedWindow("Select centers", cv2.WINDOW_NORMAL)
        cv2.imshow("Select centers", img)
        cv2.setMouseCallback("Select centers", select_point)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        if len(centers) != 2:
            print(f"Warning: Only {len(centers)} points selected in {fname}. Skipping.")
            return []

        return centers


    def _auto_detect_objects(self, img):
        """
          Automatically detect object centers via thresholding and contour centroids.

          Steps:
            1. Convert to grayscale.
            2. Blur to reduce noise.
            3. Apply Otsu’s threshold (inverted) to segment objects.
            4. Find external contours.
            5. For each contour with area ≥ 500 px², compute its centroid.

          Args:
              img: The input BGR image.

          Returns:
              A list of (x, y) centroids, sorted left-to-right by x-coordinate.
          """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        object_centers = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 500:  # filter out noise
                continue
            M = cv2.moments(cnt)
            if M['m00'] == 0:
                continue
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            object_centers.append((cx, cy))

        # Optionally sort by x to keep order consistent
        object_centers = sorted(object_centers, key=lambda x: x[0])
        return object_centers

    def get_centers(self):
        """
                Retrieve the mapping of image filenames to detected centers.

                Returns:
                    Dictionary where each key is a filename and each value is the list
                    of detected (x, y) centers in that image.
                """
        return self.centers_per_image

