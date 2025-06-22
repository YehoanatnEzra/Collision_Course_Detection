import cv2
import os

class ClickCollector:
    """
    Utility to let the user click on an object in a series of images
    and collect those (x, y) pixel coordinates.
    """

    def __init__(self, image_folder: str = "images", output_file: str = "clicked_points.txt",
                 extensions: tuple = (".jpg", ".png", ".jpeg")):
        self.image_folder = image_folder
        self.output_file = output_file
        self.extensions = extensions
        self.clicked_points = []

    def _click_event(self, event, x, y, flags, img):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"Clicked at: ({x}, {y})")
            self.clicked_points.append((x, y))
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)

    def run(self):
        """Load images, allow user to click on each, then save points."""
        for filename in sorted(os.listdir(self.image_folder)):
            if filename.lower().endswith(self.extensions):
                path = os.path.join(self.image_folder, filename)
                img = cv2.imread(path)
                if img is None:
                    continue

                print(f"\nClick on the object in: {filename}")
                img_copy = img.copy()
                cv2.imshow("Image", img_copy)
                cv2.setMouseCallback("Image", lambda e, x, y, f, p=img_copy: self._click_event(e, x, y, f, p))
                cv2.waitKey(0)

        cv2.destroyAllWindows()
        self._save_points()

    def _save_points(self):
        """Save clicked points to output file."""
        with open(self.output_file, "w") as f:
            for pt in self.clicked_points:
                f.write(f"{pt[0]},{pt[1]}\n")
        print(f"All points saved to {self.output_file}")


if __name__ == "__main__":
    collector = ClickCollector()
    collector.run()
