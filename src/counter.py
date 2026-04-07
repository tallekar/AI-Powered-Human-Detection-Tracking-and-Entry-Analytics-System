from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Tuple


BoundingBox = Tuple[int, int, int, int]
Point = Tuple[int, int]


@dataclass
class TrackedDetection:
    track_id: int
    box: BoundingBox
    confidence: float


@dataclass
class EntryEvent:
    track_id: int
    crossed_at: datetime
    centroid_x: int
    centroid_y: int
    box_x: int
    box_y: int
    box_w: int
    box_h: int
    direction: str = "in"


@dataclass
class Track:
    track_id: int
    centroid: Point
    previous_centroid: Point
    box: BoundingBox
    missed_frames: int = 0
    counted: bool = False

    def update(self, centroid: Point, box: BoundingBox) -> None:
        self.previous_centroid = self.centroid
        self.centroid = centroid
        self.box = box
        self.missed_frames = 0


@dataclass
class CounterStats:
    total_entered: int = 0
    male_count: int = 0
    female_count: int = 0


@dataclass
class PeopleCounter:
    line_y: int
    max_missed_frames: int = 15
    tracks: Dict[int, Track] = field(default_factory=dict)
    stats: CounterStats = field(default_factory=CounterStats)

    def update(self, detections: List[TrackedDetection]) -> List[EntryEvent]:
        seen_track_ids = set()
        entry_events: List[EntryEvent] = []

        for detection in detections:
            centroid = self._centroid(detection.box)
            seen_track_ids.add(detection.track_id)

            track = self.tracks.get(detection.track_id)
            if track is None:
                track = Track(
                    track_id=detection.track_id,
                    centroid=centroid,
                    previous_centroid=centroid,
                    box=detection.box,
                )
                self.tracks[detection.track_id] = track
            else:
                track.update(centroid, detection.box)

            event = self._maybe_count_entry(track)
            if event is not None:
                entry_events.append(event)

        stale_ids = []
        for track_id, track in self.tracks.items():
            if track_id not in seen_track_ids:
                track.missed_frames += 1
                if track.missed_frames > self.max_missed_frames:
                    stale_ids.append(track_id)

        for track_id in stale_ids:
            del self.tracks[track_id]

        return entry_events

    def attach_gender_counts(self, male_count: int, female_count: int) -> None:
        self.stats.male_count = male_count
        self.stats.female_count = female_count

    def _maybe_count_entry(self, track: Track) -> EntryEvent | None:
        if track.counted:
            return None

        previous_y = track.previous_centroid[1]
        current_y = track.centroid[1]

        if previous_y < self.line_y <= current_y:
            self.stats.total_entered += 1
            track.counted = True
            box_x, box_y, box_w, box_h = track.box
            return EntryEvent(
                track_id=track.track_id,
                crossed_at=datetime.now(timezone.utc),
                centroid_x=track.centroid[0],
                centroid_y=track.centroid[1],
                box_x=box_x,
                box_y=box_y,
                box_w=box_w,
                box_h=box_h,
            )

        return None

    @staticmethod
    def _centroid(box: BoundingBox) -> Point:
        x, y, w, h = box
        return x + w // 2, y + h // 2
