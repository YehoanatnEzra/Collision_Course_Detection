"""
scene_editor.py

A modular pipeline for applying batch edits to entire “scenes” of images.

Each scene is a subfolder under `input_root`, and each editing operation
is implemented as a method on SceneEditor.  All operations read every image
in every scene, apply the transformation, and write results under `output_root`.
"""

import os
import cv2
import numpy as np
import random

class SceneEditor:
    """
    A container for scene-level image editing operations.

    Scenes are directories under `input_root`.  Each method should:
      1. Walk every scene folder.
      2. Load each image file (JPEG/PNG).
      3. Apply the operation.
      4. Save the result under the matching path in `output_root`.

    You can add methods like:
      - rectify_perspective(dst_size)
      - color_balance(params)
      - crop_to_roi(roi)
      - resize_all(target_size)
      - apply_filter(kernel)
      - …and so on.

    Attributes:
        input_root (str):  Path to folder containing scene subdirectories.
        output_root (str): Path where edited scenes are saved.
    """
    def __init__(self, input_root, output_root):
        """
        Create a new SceneEditor pipeline.

        Args:
            input_root:  Directory containing one subfolder per scene.
            output_root: Directory to write edited scenes.  Will be created
                         if it does not already exist.
        """
        self.input_root = input_root
        self.output_root = output_root
        os.makedirs(self.output_root, exist_ok=True)

    def rectify_perspective(self, dst_size):
        """
       Define a 4-point perspective warp on one sample image, then apply it
       to all images in all scenes.

       Workflow:
         1. Randomly choose one scene folder under `input_root`.
         2. Randomly choose one image in that scene; load & display it.
         3. User clicks exactly four points (in consistent order).
         4. Compute the homography H mapping those points → rectangle of size
            dst_size (width, height).
         5. For every scene and every image, warp via cv2.warpPerspective(img, H, dst_size)
            and save under the same relative path in `output_root`.

       Args:
           dst_size:  (width, height) of output images after warp.

       Raises:
           ValueError: If no scenes exist, no images in the chosen scene,
                       or exactly 4 points aren’t clicked.
           FileNotFoundError: If a chosen image fails to load.
       """
        # Pick a random image from the original input folder
        scenes = sorted(os.listdir(self.input_root))
        if not scenes:
            raise ValueError("No scenes found in input folder.")

        random_scene = random.choice(scenes)
        scene_path = os.path.join(self.input_root, random_scene)
        image_files = [f for f in os.listdir(scene_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not image_files:
            raise ValueError(f"No image files found in scene {random_scene}.")

        random_image = random.choice(image_files)
        example_image_path = os.path.join(scene_path, random_image)

        img = cv2.imread(example_image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found: {example_image_path}")

        points = []

        def select_point(event, x, y):
            if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
                points.append((x, y))
                print(f"Point {len(points)}: ({x}, {y})")
                cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
                cv2.imshow("Select 4 points", img)

        print(f"Select 4 points from image: {example_image_path}")
        cv2.namedWindow("Select 4 points", cv2.WINDOW_NORMAL)
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

        for scene in sorted(os.listdir(self.input_root)):
            scene_path = os.path.join(self.input_root, scene)
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
    output_root = "/cs/usr/luna/PycharmProjects/3D_final_project/Scenes_Final"
    sample_image_path = "/cs/usr/luna/PycharmProjects/3D_final_project/Scenes/scene3_collision/a.jpeg"
    img = cv2.imread(sample_image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {sample_image_path}")
    original_size = (img.shape[1], img.shape[0])  # width, height

    editor = SceneEditor(input_root, output_root)
    editor.rectify_perspective(original_size)
