# cross_ratio_collision/analyze_collision.py

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional, List


def analyze_collision(
    ship_a_points: np.ndarray,
    ship_b_points: np.ndarray,
    plot_path: str,
    time_threshold: float,
    cr_eps: float = 0.15,   # relative tolerance ~5–15% is typical
) -> Tuple[float, Tuple[Optional[float], Optional[float], bool], Tuple[Optional[float], Optional[float], bool], bool]:
    """
    Analyze potential collision between two moving objects (ships) using:
      1) Total Least Squares (TLS/PCA) line fit for each trajectory,
      2) Geometric line intersection as candidate meeting point P,
      3) Per-ship time-of-arrival to P via 1D linear regression along the fitted direction,
      4) Cross-Ratio (CR) stability over sliding 4-frame windows (handles N=4/5/6+),
      5) A CPA (Closest Point of Approach) fallback,
      6) Visualization with fitted lines and intersection.

    Args:
        ship_a_points: (N,2) float array of 2D points (one per frame) for Ship A.
        ship_b_points: (M,2) float array of 2D points (one per frame) for Ship B.
        plot_path: path to save the visualization (PNG).
        time_threshold: max allowed |tA - tB| (in frames) for declaring collision at P.
        cr_eps: relative tolerance for declaring CR series "stable"
                (used as % window for consistency and near-target checks).

    Returns:
        (min_time_gap, cr_a_summary, cr_b_summary, collision_flag)
          - min_time_gap (float): minimal |tA - tB| at intersection P (inf if no valid times).
          - cr_a_summary = (mean, delta, stable_flag)  # mean, range (max-min), stability over sliding windows
          - cr_b_summary = (mean, delta, stable_flag)
          - collision_flag (bool): True if intersection-based test passes, or CPA fallback triggers.

    Notes:
        * If N < 4 for a ship, CR will return (None, None, False).
        * “Stable” means: the CRs from sliding windows are mutually consistent and
          (optionally) near the theoretical 4/3 expected under constant-speed sampling.
    """

    if ship_a_points.shape[0] < 2 or ship_b_points.shape[0] < 2:
        raise ValueError("Need at least 2 points per ship to fit a line.")

    MIN_SPEED = 0.25        # px/frame (along direction) — below this treat as near-static
    LOOKAHEAD = max(len(ship_a_points), len(ship_b_points)) + 6  # frames window for CPA fallback
    DIST_THRESH = 10.0      # px → “close enough” threshold for CPA fallback

    # ---------- Helpers ----------

    def fit_line_tls(pts: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Total least-squares (PCA) line fit in R^2.
        Returns:
          p0: point on the line (centroid)
          v:  unit direction vector
        """
        p0 = pts.mean(axis=0)
        X = pts - p0
        _, _, Vt = np.linalg.svd(X, full_matrices=False)
        v = Vt[0]
        v = v / (np.linalg.norm(v) + 1e-12)
        return p0, v

    def line_intersection(p0a: np.ndarray, va: np.ndarray,
                          p0b: np.ndarray, vb: np.ndarray,
                          eps: float = 1e-9) -> Tuple[Optional[np.ndarray], bool]:
        """
        Solve p0a + ta*va = p0b + tb*vb. Returns (P, parallel_flag).
        If nearly parallel → (None, True).
        """
        cross = va[0]*vb[1] - va[1]*vb[0]
        if abs(cross) < eps:
            return None, True
        A = np.column_stack((va, -vb))
        rhs = (p0b - p0a)
        ts, _, _, _ = np.linalg.lstsq(A, rhs, rcond=None)
        ta = float(ts[0])
        P = p0a + ta * va
        return P, False

    def project_1d(pts: np.ndarray, p0: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Project 2D points onto (p0, v) to get 1D coordinates along the fitted direction."""
        v = v / (np.linalg.norm(v) + 1e-12)
        return (pts - p0) @ v

    def fit_time_regression(svals: np.ndarray) -> Tuple[float, float]:
        """
        Fit s(t) = alpha + beta * t, where t = 0..N-1 (frames).
        Returns (alpha, beta). |beta| is speed along the direction (px/frame).
        """
        t = np.arange(len(svals), dtype=float)
        beta, alpha = np.polyfit(t, svals, 1)  # np.polyfit -> [slope, intercept]
        return float(alpha), float(beta)

    def time_of_point(sP: float, alpha: float, beta: float) -> Optional[float]:
        """Return t such that sP = alpha + beta*t. None if beta ~ 0."""
        if abs(beta) < 1e-12:
            return None
        return (sP - alpha) / beta

    def cross_ratio(a: float, b: float, c: float, d: float) -> float:
        """CR = ((a-c)*(b-d))/((a-d)*(b-c)) with guards."""
        den = (a - d) * (b - c)
        if abs(den) < 1e-12:
            return np.nan
        return ((a - c) * (b - d)) / den

    def cr_sliding_windows(u: np.ndarray) -> np.ndarray:
        """
        Compute CR on all consecutive 4-frame windows: (0..3), (1..4), ...
        Returns an array of finite CR values (may be empty if N<4).
        """
        N = len(u)
        if N < 4:
            return np.array([], dtype=float)
        crs = []
        for i in range(N - 3):
            v = cross_ratio(u[i], u[i+1], u[i+2], u[i+3])
            if np.isfinite(v):
                crs.append(float(v))
        return np.array(crs, dtype=float)

    def summarize_cr(u: np.ndarray, rel_tol: float, assume_const_speed: bool = True
                     ) -> Tuple[Optional[float], Optional[float], bool]:
        """
        Summarize CR consistency over sliding windows.
        Returns (mean, delta=max-min, stable_flag). If not enough data -> (None, None, False).

        Stability criteria:
          - Internal consistency: max/min <= 1+rel_tol  (if >=2 CRs exist)
          - Near target (optional): each CR within rel_tol of 4/3 (constant-speed ideal)
        """
        CRs = cr_sliding_windows(u)
        if CRs.size == 0:
            return None, None, False

        # Consistency among windows
        consistent = True
        if CRs.size >= 2:
            consistent = (CRs.max() / max(CRs.min(), 1e-12)) <= (1.0 + rel_tol)

        # Near-theoretical target 4/3 if assuming constant-speed equal-time sampling
        near_target = True
        if assume_const_speed:
            target = 4.0 / 3.0
            near_target = np.all(np.abs(CRs - target) <= rel_tol * target)

        stable = bool(consistent and near_target)
        return float(CRs.mean()), float(CRs.max() - CRs.min()), stable

    def is_future_time(t: Optional[float], n: int, tol: float = 1e-9) -> bool:
        """True if the event time is in the future relative to the last observed frame (index n-1)."""
        return (t is not None) and np.isfinite(t) and (t >= -tol) and (t >= (n - 1) - tol)

    # ---------- Fit TLS lines ----------
    p0_a, v_a = fit_line_tls(ship_a_points)
    p0_b, v_b = fit_line_tls(ship_b_points)

    # ---------- Intersection ----------
    P, parallel = line_intersection(p0_a, v_a, p0_b, v_b)

    # ---------- 1D projections & time regression ----------
    s_a = project_1d(ship_a_points, p0_a, v_a)
    s_b = project_1d(ship_b_points, p0_b, v_b)
    alpha_a, beta_a = fit_time_regression(s_a)
    alpha_b, beta_b = fit_time_regression(s_b)

    near_static_a = abs(beta_a) < MIN_SPEED
    near_static_b = abs(beta_b) < MIN_SPEED

    # ---------- Time-of-arrival to P ----------
    tA = tB = None
    min_time_gap = float("inf")
    ahead_a = ahead_b = False

    if P is not None:
        sP_a = project_1d(P[None, :], p0_a, v_a)[0]
        sP_b = project_1d(P[None, :], p0_b, v_b)[0]

        tA = time_of_point(sP_a, alpha_a, beta_a)
        tB = time_of_point(sP_b, alpha_b, beta_b)

        if (tA is not None) and (tB is not None) and np.isfinite(tA) and np.isfinite(tB):
            min_time_gap = abs(tA - tB)

        ahead_a = is_future_time(tA, len(s_a))
        ahead_b = is_future_time(tB, len(s_b))

    # ---------- Cross-Ratio summaries (independent of P) ----------
    cr_a = summarize_cr(s_a, rel_tol=cr_eps, assume_const_speed=True)
    cr_b = summarize_cr(s_b, rel_tol=cr_eps, assume_const_speed=True)

    # ---------- Primary collision decision (intersection-based) ----------
    collision = (P is not None) and (min_time_gap < time_threshold) and ahead_a and ahead_b

    # ---------- CPA fallback in the image plane ----------
    def closest_approach(p0a, va, aa, ba, p0b, vb, ab, bb):
        # Positions as functions of (continuous) frame index t:
        # qA(t) = p0a + (aa + ba*t) * va
        # qB(t) = p0b + (ab + bb*t) * vb
        C0 = (p0a + aa*va) - (p0b + ab*vb)
        C1 = ba*va - bb*vb
        denom = float(np.dot(C1, C1))
        if denom < 1e-12:
            # Relative velocity ~0 → distance barely changes; pick t=0
            t_star = 0.0
            qA = p0a + (aa + ba*t_star) * va
            qB = p0b + (ab + bb*t_star) * vb
            return t_star, float(np.linalg.norm(qA - qB))
        t_star = - float(np.dot(C0, C1)) / denom
        qA = p0a + (aa + ba*t_star) * va
        qB = p0b + (ab + bb*t_star) * vb
        return t_star, float(np.linalg.norm(qA - qB))

    t_star, d_star = closest_approach(p0_a, v_a, alpha_a, beta_a, p0_b, v_b, alpha_b, beta_b)
    within_time = (0.0 <= t_star <= LOOKAHEAD)
    near_enough = (d_star <= DIST_THRESH)

    if (not collision) and within_time and near_enough:
        collision = True
        print(f"[Fallback] CPA triggered: t*={t_star:.2f} frames, d*={d_star:.1f} px")
    else:
        print(f"[Fallback] CPA: t*={t_star:.2f}, d*={d_star:.1f} (no trigger)")

    # ---------- Visualization ----------
    _save_plot(
        ship_a_points, ship_b_points,
        p0_a, v_a, p0_b, v_b,
        P, collision, plot_path
    )

    # ---------- Console diagnostics ----------
    print(f"Predicted arrival times: tA={tA if tA is not None else '∞'} , tB={tB if tB is not None else '∞'} (frames)")
    print(f"Minimal time gap: {min_time_gap:.3f} frames  (threshold = {time_threshold})")
    print(f"Ship A CR → mean={cr_a[0]}, Δ={cr_a[1]}, stable={cr_a[2]}")
    print(f"Ship B CR → mean={cr_b[0]}, Δ={cr_b[1]}, stable={cr_b[2]}")
    print(f"Ahead flags: A={ahead_a}, B={ahead_b} | Parallel: {parallel} | Near-static: A={near_static_a}, B={near_static_b}")
    print("Collision course detected!" if collision else "No collision course.")

    return min_time_gap, cr_a, cr_b, collision


# ---------- plotting helper ----------

def _save_plot(
    ship_a_points: np.ndarray,
    ship_b_points: np.ndarray,
    p0_a: np.ndarray, v_a: np.ndarray,
    p0_b: np.ndarray, v_b: np.ndarray,
    P: Optional[np.ndarray],
    collision: bool,
    plot_path: str
) -> None:
    plt.figure(figsize=(8, 6))

    # Trajectories
    plt.plot(ship_a_points[:, 0], ship_a_points[:, 1], 'o-', label='Ship A')
    plt.plot(ship_b_points[:, 0], ship_b_points[:, 1], 'o-', label='Ship B')

    # Fitted lines (extended)
    def draw_line(p0, v, label):
        v = v / (np.linalg.norm(v) + 1e-12)
        ts = np.linspace(-500, 500, 2)
        xs = p0[0] + ts * v[0]
        ys = p0[1] + ts * v[1]
        plt.plot(xs, ys, '--', alpha=0.5, label=label)

    draw_line(p0_a, v_a, 'A fit')
    draw_line(p0_b, v_b, 'B fit')

    if P is not None:
        plt.scatter(P[0], P[1], s=80, label='Intersection P', zorder=5)

    title_color = 'red' if collision else 'green'
    title = f"{'Collision risk' if collision else 'No collision'}"
    plt.title(title, color=title_color, fontsize=15, fontweight='bold')
    plt.gca().title.set_bbox(dict(facecolor='white', edgecolor=title_color, boxstyle='round,pad=0.3'))

    plt.xlabel("X (pixels)")
    plt.ylabel("Y (pixels)")
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(plot_path, dpi=130)
    plt.close()
