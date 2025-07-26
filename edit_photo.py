import os
import cv2
import numpy as np
import random

class SceneEditor:
    def __init__(self, input_root, crop_root, output_root):
        self.input_root = input_root
        self.crop_root = crop_root
        self.output_root = output_root
        os.makedirs(self.crop_root, exist_ok=True)
        os.makedirs(self.output_root, exist_ok=True)

    def crop_and_resize_images(self, roi, resize_to=None):
        for scene in sorted(os.listdir(self.input_root)):
            scene_path = os.path.join(self.input_root, scene)
            out_path = os.path.join(self.crop_root, scene)
            os.makedirs(out_path, exist_ok=True)
            for fname in sorted(os.listdir(scene_path)):
                if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                img = cv2.imread(os.path.join(scene_path, fname))
                if img is None:
                    continue

                x, y, w, h = roi
                cropped = img[y:y+h, x:x+w]

                if resize_to:
                    resized = cv2.resize(cropped, resize_to)
                else:
                    resized = cropped

                cv2.imwrite(os.path.join(out_path, fname), resized)

    def rectify_perspective(self, dst_size):
        # Pick a random image from the cropped folder
        scenes = sorted(os.listdir(self.crop_root))
        if not scenes:
            raise ValueError("No scenes found in cropped folder.")

        random_scene = random.choice(scenes)
        scene_path = os.path.join(self.crop_root, random_scene)
        image_files = [f for f in os.listdir(scene_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not image_files:
            raise ValueError(f"No image files found in scene {random_scene}.")

        random_image = random.choice(image_files)
        example_image_path = os.path.join(scene_path, random_image)

        img = cv2.imread(example_image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found: {example_image_path}")

        points = []

        def select_point(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
                points.append((x, y))
                print(f"Point {len(points)}: ({x}, {y})")
                cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
                cv2.imshow("Select 4 points", img)

        print(f"Select 4 points from image: {example_image_path}")
        cv2.imshow("Select 4 points", img)
        cv2.setMouseCallback("Select 4 points", select_point)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        if len(points) != 4:
            raise ValueError("You must select exactly 4 points.")

        src_pts = np.float32(points)
        dst_w, dst_h = dst_size
        dst_pts = np.float32([[0, 0], [dst_w, 0], [dst_w, dst_h], [0, dst_h]])
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)

        for scene in sorted(os.listdir(self.crop_root)):
            scene_path = os.path.join(self.crop_root, scene)
            out_path = os.path.join(self.output_root, scene)
            os.makedirs(out_path, exist_ok=True)
            for fname in sorted(os.listdir(scene_path)):
                if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                img = cv2.imread(os.path.join(scene_path, fname))
                if img is None:
                    continue
                warped = cv2.warpPerspective(img, M, dst_size)
                cv2.imwrite(os.path.join(out_path, fname), warped)


if __name__ == '__main__':
    input_root  = "/cs/usr/luna/PycharmProjects/3D_final_project/Scenes"
    crop_root   = "/cs/usr/luna/PycharmProjects/3D_final_project/Scenes_Cropped"
    output_root = "/cs/usr/luna/PycharmProjects/3D_final_project/Scenes_Final"

    editor = SceneEditor(input_root, crop_root, output_root)

    # שלב א': חיתוך
    editor.crop_and_resize_images(roi=(20, 110, 750, 1100), resize_to=(750, 1200))
    


    editor.rectify_perspective((750, 1200))
