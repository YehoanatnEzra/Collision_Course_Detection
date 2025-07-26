from ship_detector import ShipDetector
from collision_analyzer import CollisionAnalyzer

detector = ShipDetector("Scenes_Final/scene3_collision")
detector.process_scene("manual")
centers = detector.get_centers()

analyzer = CollisionAnalyzer(centers)
analyzer.analyze()
analyzer.plot()

if analyzer.is_collision_course():
    print("Change course! Ships are on a collision course!!")
else:
    print("keep course and speed, No collision course detected.")
