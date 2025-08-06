from cross_ratio_collision.manual_track_points import manually_track_ships
from cross_ratio_collision.analyze_collision import analyze_collision

import os

TIME_THRESHOLD = 3.5  # this is according to the size of the "ship


def main(scene_path):
    """
    Main entry point for te Cross-Ratio collision detection demo.

    Workflow:
      1. Manually click one point per ship in each frame.
      2. Compute the minimal time gap and cross–ratios.
      3. Save a plot of the two ship trajectories and intersection.
      4. Print out metrics and a collision vs. no-collision verdict.
    """
    # Let the user click exactly one point per ship in each frame, returns two Nx2 arrays: ship_a_pts and ship_b_pts
    ship_a_pts, ship_b_pts = manually_track_ships(scene_path)

    print("\nShip A points:", ship_a_pts)
    print("Ship B points:", ship_b_pts)

    # Ensure an output folder exists for results
    os.makedirs("results", exist_ok=True)
    plot_path = os.path.join("results", "cross_ratio_result.png")

    time_gap, cr_a, cr_b, collision = analyze_collision(ship_a_pts, ship_b_pts, plot_path,TIME_THRESHOLD)

    # Print out the computed metrics
    print(f"\nMinimal time gap: {time_gap:.2f} frames")
    print(f"Cross Ratio A: {cr_a:.4f}")
    print(f"Cross Ratio B: {cr_b:.4f}")

    # Use the returned flag to decide collision vs. safe
    if collision:
        print("Potential collision detected!")
    else:
        print("No collision course detected.")


if __name__ == "__main__":
    # Scene 1 - collision
    scene1_path = r"C:\Users\Nira\Desktop\Yehonatan\3D\Mine\Collision_Course_Detection-main\scenes\pre_rectified_scenes\scene1_collision"

    # Scene 2 - No collision
    scene2_path = r"C:\Users\Nira\Desktop\Yehonatan\3D\Mine\Collision_Course_Detection-main\scenes\pre_rectified_scenes\scene2_noCollision"

    # Scene 3 - Collision
    scene3_path = r"C:\Users\Nira\Desktop\Yehonatan\3D\Mine\Collision_Course_Detection-main\scenes\pre_rectified_scenes\scene3_collision"

    # Scene 4 - No collision
    scene4_path = r"C:\Users\Nira\Desktop\Yehonatan\3D\Mine\Collision_Course_Detection-main\scenes\pre_rectified_scenes\scene4-noCollision"

    # Scene 5 - Collision
    scene5_path = r"C:\Users\Nira\Desktop\Yehonatan\3D\Mine\Collision_Course_Detection-main\scenes\pre_rectified_scenes\scene5_collision"

    main(scene5_path)  # Choose any scene you’d like.
