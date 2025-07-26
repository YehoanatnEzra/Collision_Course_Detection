
# 🚢 Collision Course Detection from Images 
This project detects whether two ships (represented by objects in a scene) are on a collision course — by analyzing a sequence of images taken from a fixed camera.

## Motivation
Inspired by maritime safety applications, this project demonstrates how computer vision techniques can be used to:
- Rectify image perspective
- Track object positions across frames
- Analyze geometry (distance and angle)
- Predict future collision based on motion trends

The project puts into practice topics covered in the course such as:
- Perspective warping
- Manual and automatic feature localization
- Geometric reasoning (distance, angle over time)
- Visualization and analysis

## 🛠 How It Works
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
