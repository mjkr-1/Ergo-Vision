from ..config import (
    HEAD_TILT_WARNING_DEGREES,
    HEAD_TILT_BAD_DEGREES,
    SHOULDER_ALIGNMENT_WARNING_DEGREES,
    SHOULDER_ALIGNMENT_BAD_DEGREES,
    NECK_OFFSET_WARNING,
    NECK_OFFSET_BAD,
    FORWARD_HEAD_WARNING,
    FORWARD_HEAD_BAD,
)
from .measurements import ErgonomicMeasurements
from .scoring import compute_score


class FeedbackEngine:
    def generate(self, m: ErgonomicMeasurements, status: str) -> list[str]:
        if not m.person_detected:
            return ["No person detected. Position yourself in front of the camera."]

        messages = []

        if m.head_tilt_degrees >= HEAD_TILT_BAD_DEGREES:
            messages.append(("BAD", "Your head is tilted significantly. Straighten your head to face the screen directly."))
        elif m.head_tilt_degrees >= HEAD_TILT_WARNING_DEGREES:
            messages.append(("WARNING", "Your head is tilted slightly. Try to keep your head level."))

        if m.shoulder_alignment_degrees >= SHOULDER_ALIGNMENT_BAD_DEGREES:
            messages.append(("BAD", "Your shoulders are uneven. Try to level them by sitting up straighter."))
        elif m.shoulder_alignment_degrees >= SHOULDER_ALIGNMENT_WARNING_DEGREES:
            messages.append(("WARNING", "Your shoulders are slightly uneven. Adjust your posture to align them."))

        if abs(m.neck_offset) >= NECK_OFFSET_BAD:
            direction = "left" if m.neck_offset < 0 else "right"
            messages.append(("BAD", f"Your head is leaning to the {direction}. Center your head over your shoulders."))
        elif abs(m.neck_offset) >= NECK_OFFSET_WARNING:
            direction = "left" if m.neck_offset < 0 else "right"
            messages.append(("WARNING", f"Your head is slightly to the {direction}. Try to center it over your spine."))

        if m.forward_head_indicator >= FORWARD_HEAD_BAD:
            messages.append(("BAD", "Your head is jutting forward. Pull your head back over your shoulders."))
        elif m.forward_head_indicator >= FORWARD_HEAD_WARNING:
            messages.append(("WARNING", "Your head is leaning forward slightly. Tuck your chin and sit back."))

        if not messages:
            if status == "GOOD":
                return ["Your posture looks good. Keep it up!"]
            return ["Maintain an upright posture with your head centered."]

        messages.sort(key=_severity_order)
        return [msg for _, msg in messages[:3]]


def _severity_order(item):
    return {"BAD": 0, "WARNING": 1}.get(item[0], 2)