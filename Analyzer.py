import os
import math
import cv2
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

class Analyzer:
    def __init__(self, clicked_file, image_folder, focal_length=None):
        """
        Analyzer for bearing angle across a sequence of images.

        Parameters:
        - clicked_file: path to 'clicked_points.txt' containing x,y per line
        - image_folder: folder containing images (will be sorted alphabetically)
        - focal_length: focal length in pixels; if None, defaults to half the image width
        """
        self.image_folder = image_folder
        # Load saved click coordinates
        with open(clicked_file, 'r') as f:
            self.points = [
                tuple(map(int, line.strip().split(',')))
                for line in f if line.strip()
            ]
        self.f = focal_length

    def compute_angles(self):
        """
        Compute the horizontal bearing angle θ for each clicked point.

        Returns:
        - A list of angles (in degrees), one per image
        """
        angles = []
        # Gather and sort image filenames
        filenames = sorted(
            fn for fn in os.listdir(self.image_folder)
            if fn.lower().endswith(('.png', '.jpg', '.jpeg'))
        )
        if len(filenames) != len(self.points):
            raise ValueError(
                f"Number of images ({len(filenames)}) and clicked points "
                f"({len(self.points)}) do not match."
            )

        for idx, filename in enumerate(filenames):
            x, y = self.points[idx]
            img_path = os.path.join(self.image_folder, filename)
            img = cv2.imread(img_path)
            if img is None:
                raise FileNotFoundError(f"Cannot load image '{img_path}'")
            h, w = img.shape[:2]
            cx, cy = w / 2, h / 2
            f = self.f if self.f is not None else (w / 2)
            # Bearing angle θ = atan2(Δx, f)
            theta = math.degrees(math.atan2((x - cx), f))
            angles.append(theta)

        return angles

    def plot_angles(self, angles, tolerance_deg=1.0):
        """
        Plot the bearing angles and report stability.

        Parameters:
        - angles: list of angles in degrees
        - tolerance_deg: maximum allowed deviation from the initial angle
        """
        plt.figure(figsize=(8, 4))
        plt.plot(angles, marker='o')
        plt.axhline(angles[0] + tolerance_deg, color='red', linestyle='--')
        plt.axhline(angles[0] - tolerance_deg, color='red', linestyle='--')
        plt.title(f"Bearing Angle Across Images (±{tolerance_deg}° tolerance)")
        plt.xlabel("Image Index")
        plt.ylabel("Angle (degrees)")
        plt.grid(True)
        plt.show()

        angle_range = max(angles) - min(angles)
        if angle_range <= 2 * tolerance_deg:
            print(f"Stable bearing: variation = {angle_range:.2f}°")
        else:
            print(f"Unstable bearing: variation = {angle_range:.2f}° exceeds tolerance")

if __name__ == "__main__":
    analyzer = Analyzer("clicked_points.txt", "images", focal_length=None)
    angles = analyzer.compute_angles()
    print("Computed angles:", ["{:.2f}°".format(a) for a in angles])
    analyzer.plot_angles(angles, tolerance_deg=1.0)
