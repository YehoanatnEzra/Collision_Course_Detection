import math
import matplotlib.pyplot as plt

ANGLE_THRESHOLD = 8

class CollisionAnalyzer:
    def __init__(self, centers_per_image):
        self.centers_per_image = centers_per_image  # dict: filename -> [(x1, y1), (x2, y2)]
        self.distances = []
        self.angles = []
        self.filenames = []

    def analyze(self):
        for fname in sorted(self.centers_per_image.keys()):
            centers = self.centers_per_image[fname]
            if len(centers) != 2:
                continue

            (x1, y1), (x2, y2) = centers
            dx = x2 - x1
            dy = y2 - y1

            distance = math.sqrt(dx**2 + dy**2)
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)

            self.distances.append(distance)
            self.angles.append(angle_deg)
            self.filenames.append(fname)

    def plot(self):
        fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

        ax[0].plot(self.filenames, self.distances, marker='o')
        ax[0].set_ylabel("Distance")
        ax[0].set_title("Distance between ships over time")

        ax[1].plot(self.filenames, self.angles, marker='o', color='orange')
        ax[1].set_ylabel("Angle (deg)")
        ax[1].set_title("Angle between ships over time")
        ax[1].set_xticks(range(len(self.filenames)))
        ax[1].set_xticklabels(self.filenames, rotation=45, ha='right')

        plt.tight_layout()
        plt.show()

    def is_collision_course(self, angle_threshold=ANGLE_THRESHOLD, min_decreasing_steps=3):
        # angle_threshold in degrees (max allowed variation)
        # min_decreasing_steps: how many steps should distance decrease consecutively

        if len(self.distances) < min_decreasing_steps:
            return False

        angle_variation = max(self.angles) - min(self.angles)
        if angle_variation > angle_threshold:
            return False

        decreasing_count = 0
        for i in range(1, len(self.distances)):
            if self.distances[i] < self.distances[i - 1]:
                decreasing_count += 1
            else:
                decreasing_count = 0
            if decreasing_count >= min_decreasing_steps:
                return True

        return False
