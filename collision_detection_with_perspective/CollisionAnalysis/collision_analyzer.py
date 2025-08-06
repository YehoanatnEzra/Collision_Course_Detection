# collision_analyzer.py

"""
Analyze pairwise ship-center data to determine potential collision courses.

This module provides the CollisionAnalyzer class, which:
  - Computes the Euclidean distance and bearing angle between two detected
    ship centers in each frame (image).
  - Plots the distance and angle over time (frame sequence).
  - Determines whether the two ships appear to be on a collision course
    based on distance trends and angle stability.
"""
import math
import matplotlib.pyplot as plt
import numpy as np

ANGLE_THRESHOLD = 8  # degrees: maximum allowed angle variation

class CollisionAnalyzer:
    """
      Compute distance & angle time series from per-image ship centers, plot them,
      and decide if the ships are on a collision course.

      Attributes:
          centers_per_image (dict[str, list[tuple[int, int]]]):
              Mapping from image filename to exactly two (x, y) centers.
          distances (list[float]): Euclidean distances between the two centers,
              in the sorted filename order.
          angles (list[float]): Bearing angles (degrees) from first to second center.
          filenames (list[str]): Filenames corresponding to each computed pair.
      """
    def __init__(self, centers_per_image):
        """
        Initialize the analyzer with detected centers.

        Args:
            centers_per_image: A dict mapping each image filename to a list of
                exactly two (x, y) tuples. Entries with != 2 points will be skipped.
        """
        self.centers_per_image = centers_per_image
        self.distances = []
        self.angles = []
        self.filenames = []

    def analyze(self):
        """
       Compute distance and angle for each image in sorted filename order.

       Populates:
         - self.distances
         - self.angles
         - self.filenames

       Skips any frames where fewer or more than two centers are provided.
       """
        for fname in sorted(self.centers_per_image.keys()):
            centers = self.centers_per_image[fname]
            if len(centers) != 2:
                continue

            (x1, y1), (x2, y2) = centers
            dx = x2 - x1
            dy = y2 - y1

            distance = math.hypot(dx, dy)
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)

            self.distances.append(distance)
            self.angles.append(angle_deg)
            self.filenames.append(fname)

    def plot(self):
        """
       Plot the computed distance and angle time series.

       Creates a 2×1 subplot:
         - Top: Distance vs. frame (filename) with markers.
         - Bottom: Angle (deg) vs. frame (filename), filenames on x-axis.
       """
        fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

        # Distance plot
        ax[0].plot(self.filenames, self.distances, marker='o')
        ax[0].set_ylabel("Distance")
        ax[0].set_title("Distance between ships over time")

        # Angle plot
        ax[1].plot(self.filenames, self.angles, marker='o', color='orange')
        ax[1].set_ylabel("Angle (deg)")
        ax[1].set_title("Angle between ships over time")
        ax[1].set_xticks(range(len(self.filenames)))
        ax[1].set_xticklabels(self.filenames, rotation=45, ha='right')

        plt.tight_layout()
        plt.show()

    def is_collision_course(self, angle_threshold=ANGLE_THRESHOLD, min_decreasing_steps=2):
        """
           Decide if the two ships appear to be on a collision course.

           Criteria:
             1. At least `min_decreasing_steps` consecutive frames where distance
                decreases.
             2. Overall variation in bearing angle ≤ `angle_threshold` degrees.

           Args:
               angle_threshold: Maximum allowed (max–min) angle variation (degrees).
               min_decreasing_steps: Number of consecutive frames with strictly
                   decreasing distances required.

           Returns:
               True if both criteria are met, False otherwise.
           """

        # 1. Not enough data to see a trend
        if len(self.distances) < min_decreasing_steps:
            return False

        # 2. Compute angle variation using unwrapped angles to avoid ±180° jumps
        angles_rad = np.deg2rad(self.angles)
        angles_unwrapped = np.unwrap(angles_rad)
        angles_deg = np.rad2deg(angles_unwrapped)
        angle_variation = max(angles_deg) - min(angles_deg)
        if angle_variation > angle_threshold:
            return False

        # 3. Check for at least `min_decreasing_steps` consecutive decreasing distances
        decreasing_count = 0
        for i in range(1, len(self.distances)):
            if self.distances[i] < self.distances[i - 1]:
                decreasing_count += 1
            else:
                decreasing_count = 0
            if decreasing_count >= min_decreasing_steps:
                return True

        # 4. No sufficient decreasing trend => not on collision course
        return False
