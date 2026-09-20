from app.vision.landmarks import Landmark2D, LandmarkSet
from app.vision.quality import assess_tracking


def sample():
    return LandmarkSet(landmarks={
        "nose_tip": Landmark2D(.5,.3,visibility=1,presence=1),
        "left_eye_outer": Landmark2D(.45,.28,visibility=1,presence=1),
        "right_eye_outer": Landmark2D(.55,.28,visibility=1,presence=1),
        "chin": Landmark2D(.5,.38,visibility=1,presence=1),
        "forehead": Landmark2D(.5,.22,visibility=1,presence=1),
        "left_shoulder": Landmark2D(.38,.5,visibility=1,presence=1),
        "right_shoulder": Landmark2D(.62,.5,visibility=1,presence=1),
        "left_hip": Landmark2D(.42,.82,visibility=1,presence=1),
        "right_hip": Landmark2D(.58,.82,visibility=1,presence=1),
    })


def test_excellent_tracking():
    assert assess_tracking(sample()).quality == "EXCELLENT"


def test_missing_shoulder_not_reliable():
    landmarks = sample()
    del landmarks.landmarks["left_shoulder"]
    assert not assess_tracking(landmarks).reliable
