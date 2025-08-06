"""
This script demonstrates how to use the ship collision detection package.

It includes:
1. (Optional) Perspective rectification using `SceneEditor`
2. Manual collision analysis using `Run_collision_analysis`

To run:
- Uncomment `pre_processing()` if rectification is needed
- Provide the path to each scene (rectified image folder)
- Choose "manual" mode to manually select ship centers per image

Developed as part of a final project in Computer Vision
"""
from CollisionAnalysis.run_collision_analysis import Run_collision_analysis
from SceneEditor.scene_editor import SceneEditor
import cv2


def pre_processing():
    """
    Optional: Rectify the perspective of all scenes before performing collision analysis.
    This step should be done once before running the analysis.

    It allows the user to manually select 4 points in one image to create a homography
    that corrects the perspective for the entire dataset.
    """
    input_root = "/cs/usr/luna/PycharmProjects/3D_final_project/pre_rectified_scenes"
    output_root = "/cs/usr/luna/PycharmProjects/3D_final_project/post_rectified_scenes"
    sample_image_path = "/cs/usr/luna/PycharmProjects/3D_final_project/pre_rectified_scenes/scene3_collision/a.jpeg"
    img = cv2.imread(sample_image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {sample_image_path}")
    original_size = (img.shape[1], img.shape[0])  # width, height

    editor = SceneEditor(input_root, output_root)
    editor.rectify_perspective(original_size)


if __name__ == '__main__':
    """
    Main entry point for running collision analysis.

    Step 1 (optional):
        Run pre_processing() to apply perspective rectification to all scenes.
        This step has already been completed, so it's commented out.

    Step 2:
        For each scene (collision and non-collision), run the collision analysis.
        The mode "manual" means the user will be asked to manually click the two ship centers per image.
    """

    # pre_processing()  # Already completed

    # Collision scenes (should detect collision):
    Run_collision_analysis.run(
        "/cs/usr/luna/PycharmProjects/3D_final_project/post_rectified_scenes/scene1_collision",
        "manual")

    Run_collision_analysis.run(
        "/cs/usr/luna/PycharmProjects/3D_final_project/post_rectified_scenes/scene3_collision",
        "manual")

    Run_collision_analysis.run(
        "/cs/usr/luna/PycharmProjects/3D_final_project/post_rectified_scenes/scene5_collision",
        "manual")

    # Non-collision scenes (should not detect collision):
    Run_collision_analysis.run(
        "/cs/usr/luna/PycharmProjects/3D_final_project/post_rectified_scenes/scene6_noCollision",
        "manual")

    Run_collision_analysis.run(
        "/cs/usr/luna/PycharmProjects/3D_final_project/post_rectified_scenes/scene2_noCollision",
        "manual")

    Run_collision_analysis.run(
        "/cs/usr/luna/PycharmProjects/3D_final_project/post_rectified_scenes/scene4_noCollision",
        "manual")
