
import cv2
import os
import numpy as np
from typing import Tuple, List


def manually_track_ships(scene_dir: str) -> tuple[np.ndarray, np.ndarray]:
    """
    For each image in the scene, let the user manually select one point for each ship.

    Args:
        scene_dir (str): Path to the folder containing the scene images (JPEG/PNG)

    Returns:
        ship_a_points (np.ndarray): Array of shape (N, 2) with tracked points for ship A
        ship_b_points (np.ndarray): Array of shape (N, 2) with tracked points for ship B
    """
    ship_a: List[tuple[int, int]] = []
    ship_b: List[tuple[int, int]] = []

    # Load and sort image files
    files = sorted([f for f in os.listdir(scene_dir)if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

    for fname in files:
        img_path = os.path.join(scene_dir, fname)
        img = cv2.imread(img_path)
        if img is None:
            print(f"Skipped {fname} (could not load image)")
            continue

        display_img = img.copy()
        points: List[tuple[int, int]] = []

        instructions = (
            "Click on Ship A (red), then Ship B (green). "
            "Press 'u' to undo last click, 'q' to skip image."
        )

        def click_event(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                if len(points) < 2:
                    points.append((x, y))
                    color = (0, 0, 255) if len(points) == 1 else (0, 255, 0)
                    cv2.circle(display_img, (x, y), 6, color, -1)
                    cv2.imshow(window_name, display_img)

        window_name = "Click on Ship A (red), then Ship B (green)"
        # Create & size the window for each image
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1200, 800)

        # Put overlay text with instructions
        overlay = display_img.copy()
        cv2.putText(overlay, instructions, (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
        display_img = overlay

        cv2.imshow(window_name, display_img)
        cv2.setMouseCallback(window_name, click_event)

        print(f"\n📷 {fname}: {instructions}")
        # Wait until two clicks are collected (or 'q' pressed)
        while True:
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                break
            if key == ord('u'):
                if points:
                    points.pop()
                    display_img = img.copy()
                    overlay = display_img.copy()
                    cv2.putText(overlay, instructions, (30, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
                    display_img = overlay
                    for idx, (px, py) in enumerate(points):
                        color = (0, 0, 255) if idx == 0 else (0, 255, 0)
                        cv2.circle(display_img, (px, py), 6, color, -1)
                    cv2.imshow(window_name, display_img)
            if len(points) >= 2:
                break

        # Close only this window so the next one can open
        cv2.destroyWindow(window_name)

        if len(points) == 2:
            ship_a.append(points[0])
            ship_b.append(points[1])
        else:
            print(f"Skipped {fname} (need exactly 2 clicks)")

    return np.array(ship_a, dtype=float), np.array(ship_b, dtype=float)
