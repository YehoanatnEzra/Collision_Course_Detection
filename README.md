
# 🚢 Collision Course Detection from Images - 3D Project.

This repository offers two complementary pipelines for detecting whether two ships (or any two objects) in a scene are on a collision course, using a sequence of images from a fixed camera:

1. **Full CV Pipeline** — Perspective Rectification → Manual Tracking → Geometric Analysis → Collision Flag  
2. **Lightweight Pipeline** — Manual Tracking → Linear Intersection + Time-to-Collision + Cross-Ratio → Collision Flag

---


## How It Works
1. **Perspective Rectification**  
   The user selects 4 points in one image to warp all frames to a consistent top-down view.
2. **Manual Object Center Selection**  
   For each frame in a scene, the user clicks on the centers of the two ships (or shoes!).
3. **Geometric Analysis**  
   The program computes:
   - Distance between ships in each frame
   - Relative angle between them
   - Trend of distance and angle over time
4. **Collision Prediction**  
   If the angle remains consistent and distance decreases steadily, the program flags a collision course.

<img width="999" height="599" alt="Figure_1" src="https://github.com/user-attachments/assets/5110140e-b91c-4dfa-b4b4-4bc19a01c965" />
