"""
run_collision_analysis.py

Orchestrates the full pipeline: ship detection (auto or manual) and collision analysis.

This script loads all images from a scene folder, detects ship centers per frame,
computes distance & angle time series, plots the results, and finally reports
whether the ships appear to be on a collision course.
"""
from .ship_detector import ShipDetector
from .collision_analyzer import CollisionAnalyzer

class Run_collision_analysis:
    def run(scene_path, mode="auto"):
        """
        Execute the full ship-detection and collision-analysis pipeline on one scene.

        Note:
            The scene images **must** already be perspective-rectified before calling this.
            In other words, point your `scene_path` at a folder of pre-rectified frames.

        Args:
        scene_path:   Path to the directory containing the **perspective-rectified**
                      scene images.
        process_act:  Detection mode; must be either:
                          - "auto"   (automatic contour-based detection), or
                          - "manual" (click-based selection).

    Raises:
        ValueError: If `process_act` is not "auto" or "manual".
        """

        # Detect ship centers
        detector = ShipDetector(scene_path)
        detector.process_scene(mode)
        centers = detector.get_centers()

        # Analyze distances & angles
        analyzer = CollisionAnalyzer(centers)
        analyzer.analyze()

        # Visualize the results
        analyzer.plot()

        # Report collision-course verdict
        if analyzer.is_collision_course():
            print("Change course! Ships are on a collision course!!")
        else:
            print("keep course and speed, No collision course detected.")


