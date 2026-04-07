from __future__ import annotations

from typing import List

from ultralytics import YOLO

from counter import TrackedDetection


class YoloPersonDetector:
    def __init__(
        self,
        model_path: str,
        confidence: float = 0.35,
        tracker_config: str = "bytetrack.yaml",
    ) -> None:
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.tracker_config = tracker_config

    def detect(self, frame) -> List[TrackedDetection]:
        results = self.model.track(
            source=frame,
            classes=[0],
            conf=self.confidence,
            tracker=self.tracker_config,
            persist=True,
            verbose=False,
        )

        detections: List[TrackedDetection] = []
        for result in results:
            if result.boxes.id is None:
                continue

            for box in result.boxes:
                if box.id is None:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0].item())
                track_id = int(box.id[0].item())
                detections.append(
                    TrackedDetection(
                        track_id=track_id,
                        box=(
                            int(x1),
                            int(y1),
                            int(x2 - x1),
                            int(y2 - y1),
                        ),
                        confidence=confidence,
                    )
                )

        return detections


def resolve_tracker_config(tracker_name: str, tracker_config: str | None = None) -> str:
    if tracker_config:
        return tracker_config

    tracker_aliases = {
        "bytetrack": "bytetrack.yaml",
        "botsort": "botsort.yaml",
    }
    return tracker_aliases[tracker_name]
