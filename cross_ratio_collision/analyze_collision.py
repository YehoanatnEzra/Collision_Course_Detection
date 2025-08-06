import numpy as np
import matplotlib.pyplot as plt


def analyze_collision(
    ship_a_points: np.ndarray,
    ship_b_points: np.ndarray,
    plot_path: str,
    time_threshold: float
):
    """
    Analyze potential collision between two moving objects (ships),
    using linear trajectory intersection and time-to-collision.
    Saves a plot to plot_path and returns a tuple of:
        - minimal time difference (in frames)
        - Cross Ratio for Ship A (or None)
        - Cross Ratio for Ship B (or None)
        - collision (bool): True if min_time_gap < time_threshold
    """

    # Compute velocities and average velocity vectors
    vel_a = np.diff(ship_a_points, axis=0)
    vel_b = np.diff(ship_b_points, axis=0)
    avg_vel_a = vel_a.mean(axis=0)
    avg_vel_b = vel_b.mean(axis=0)

    # Fit straight lines to each trajectory
    line_a = np.polyfit(ship_a_points[:, 0], ship_a_points[:, 1], 1)
    line_b = np.polyfit(ship_b_points[:, 0], ship_b_points[:, 1], 1)

    # Compute intersection of the two lines
    m1, c1 = line_a
    m2, c2 = line_b
    x_cross = (c2 - c1) / (m1 - m2)
    y_cross = m1 * x_cross + c1
    intersection = np.array([x_cross, y_cross])

    # Compute time-to-collision for each ship
    dist_a = np.linalg.norm(ship_a_points - intersection, axis=1)
    dist_b = np.linalg.norm(ship_b_points - intersection, axis=1)
    speed_a = np.linalg.norm(avg_vel_a)
    speed_b = np.linalg.norm(avg_vel_b)
    time_a = dist_a / speed_a
    time_b = dist_b / speed_b
    time_diff = np.abs(time_a - time_b)
    min_index = np.argmin(time_diff)
    min_time_gap = time_diff[min_index]

    # Decide collision if the minimal time gap is below threshold
    collision = (min_time_gap < time_threshold)

    # Cross ratio helper functions
    def cross_ratio(a, b, c, d):
        return ((a - c) * (b - d)) / ((a - d) * (b - c))

    def project_points_1d(points, direction):
        direction = direction / np.linalg.norm(direction)
        return points @ direction

    # Compute cross ratios only if enough points are available
    min_points_required = 4
    if len(ship_a_points) >= min_points_required and len(ship_b_points) >= min_points_required:
        indices = list(range(min_points_required))
        cr_a = cross_ratio(*project_points_1d(ship_a_points[indices], avg_vel_a))
        cr_b = cross_ratio(*project_points_1d(ship_b_points[indices], avg_vel_b))
    else:
        cr_a = None
        cr_b = None
        print("⚠ Not enough points to compute cross ratio.")

    # Generate and save the plot
    plt.figure(figsize=(8, 6))
    # Plot trajectories
    plt.plot(ship_a_points[:, 0], ship_a_points[:, 1], 'bo-', label='Ship A')
    plt.plot(ship_b_points[:, 0], ship_b_points[:, 1], 'ro-', label='Ship B')
    # Plot intersection
    plt.scatter(*intersection, color='purple', label='Intersection Point', zorder=5)

    # Color title and bounding box red if collision, else green
    title_color = 'red' if collision else 'green'
    plt.title(
        "Collision Course!" if collision else "No Collision",
        color=title_color,
        fontsize=16,
        fontweight='bold'
    )
    # Optionally draw a red box around the title area
    plt.gca().title.set_bbox(dict(facecolor='white', edgecolor=title_color, boxstyle='round,pad=0.3'))

    plt.xlabel("X (pixels)")
    plt.ylabel("Y (pixels)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    # Console output
    print(f"Minimal time gap: {min_time_gap:.2f} frames  (threshold = {time_threshold})")
    if collision:
        print("Collision course detected!")
    else:
        print("No collision course.")

    return min_time_gap, cr_a, cr_b, collision
