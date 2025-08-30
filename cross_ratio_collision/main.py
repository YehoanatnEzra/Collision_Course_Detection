
from cross_ratio_collision.manual_track_points import manually_track_ships
from cross_ratio_collision.analyze_collision import analyze_collision

import os

TIME_THRESHOLD = 3.5  # frames (tune by scene scale / fps)
CR_EPS = 0.8        # tolerance for CR stability (tune per dataset)


def main(scene_path):
    """
    Main entry point for the Cross-Ratio collision detection demo.

    Workflow:
      1. Manually click one point per ship in each frame.
      2. Fit robust lines, find geometric intersection P.
      3. Estimate time-to-P for each ship and Cross-Ratio stability.
      4. Save a plot of the two ship trajectories and intersection.
      5. Print out metrics and a collision vs. no-collision verdict.
    """
    # Let the user click exactly one point per ship in each frame, returns two Nx2 arrays: ship_a_pts and ship_b_pts
    ship_a_pts, ship_b_pts = manually_track_ships(scene_path)

    print("\nShip A points:", ship_a_pts)
    print("Ship B points:", ship_b_pts)

    # Ensure an output folder exists for results
    os.makedirs("results", exist_ok=True)
    plot_path = os.path.join("results", "cross_ratio_result.png")

    time_gap, cr_a, cr_b, collision = analyze_collision(
        ship_a_pts, ship_b_pts, plot_path, TIME_THRESHOLD, cr_eps=CR_EPS
    )

    # Print out the computed metrics
    print(f"\nMinimal time gap: {time_gap:.3f} frames")
    if cr_a[0] is not None:
        print(f"Ship A — CR mean={cr_a[0]:.4f}, Δ={cr_a[1]:.4f}, stable={cr_a[2]}")
    else:
        print("Ship A — CR: insufficient data")
    if cr_b[0] is not None:
        print(f"Ship B — CR mean={cr_b[0]:.4f}, Δ={cr_b[1]:.4f}, stable={cr_b[2]}")
    else:
        print("Ship B — CR: insufficient data")

    # Use the returned flag to decide collision vs. safe
    print("\nPotential collision detected!" if collision else "\nNo collision course detected.")


if __name__ == "__main__":

    # Example: update to your local scene folder before running
    scene1_path = r"C:\Users\Nira\Desktop\Yehonatan\3D\scenes\pre_rectified_scenes\scene1_collision"

    # Scene 2 - No collision
    scene2_path = r"C:\Users\Nira\Desktop\Yehonatan\3D\scenes\pre_rectified_scenes\scene2_noCollision"

    # Scene 3 - Collision
    scene3_path = r"C:\Users\Nira\Desktop\Yehonatan\3D\scenes\pre_rectified_scenes\scene3_collision"

    # Scene 4 - No collision
    scene4_path = r"C:\Users\Nira\Desktop\Yehonatan\3D\scenes\pre_rectified_scenes\scene4-noCollision"

    # Scene 5 - Collision
    scene5_path = r"C:\Users\Nira\Desktop\Yehonatan\3D\scenes\pre_rectified_scenes\scene5_collision"
    main(scene3_path)  # Choose any scene you’d like.
