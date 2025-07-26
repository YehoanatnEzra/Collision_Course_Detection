import os
import cv2
import numpy as np

class ShipDetector:
    def __init__(self, scene_path):
        self.scene_path = scene_path
        self.centers_per_image = {}  # key: filename, value: list of centers (x, y)

    def process_scene(self,action):
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
        centers = []
        def select_point(event, x, y, flags, param):
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
        return self.centers_per_image

if __name__ == '__main__':
    scene_path = "Scenes_Final/scene3_collision"
    detector = ShipDetector(scene_path)
    detector.process_scene("manual")
    centers = detector.get_centers()
    print(centers)

