from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import cv2

from counter import PeopleCounter
from detector import YoloPersonDetector, resolve_tracker_config
from storage import EntryEventLogger, write_csv_row


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count people entering through a company gate with YOLO detection."
    )
    parser.add_argument(
        "--source",
        default="0",
        help="Camera index like 0, or a path to a video file.",
    )
    parser.add_argument(
        "--line-ratio",
        type=float,
        default=0.6,
        help="Vertical position of the entry line as a ratio of frame height.",
    )
    parser.add_argument(
        "--model",
        default="yolov8n.pt",
        help="YOLO model file to use, for example yolov8n.pt or a custom trained checkpoint.",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.35,
        help="Minimum YOLO confidence for person detections.",
    )
    parser.add_argument(
        "--database",
        default="data/gate_counter.db",
        help="SQLite database path for event logging.",
    )
    parser.add_argument(
        "--csv-log",
        default="data/entry_events.csv",
        help="CSV file path for append-only entry logs.",
    )
    parser.add_argument(
        "--camera-name",
        default="main_gate",
        help="Logical camera name stored with entry events.",
    )
    parser.add_argument(
        "--frame-width",
        type=int,
        default=960,
        help="Resize width for processing and display.",
    )
    parser.add_argument(
        "--max-missed-frames",
        type=int,
        default=15,
        help="How long a tracker ID may disappear before it is dropped from the overlay.",
    )
    parser.add_argument(
        "--tracker",
        choices=("bytetrack", "botsort"),
        default="bytetrack",
        help="Built-in tracker backend to use.",
    )
    parser.add_argument(
        "--tracker-config",
        default=None,
        help="Optional custom Ultralytics tracker config file. Overrides --tracker.",
    )
    return parser.parse_args()


def open_source(source_value: str) -> cv2.VideoCapture:
    if source_value.isdigit():
        return cv2.VideoCapture(int(source_value))
    return cv2.VideoCapture(source_value)


def ensure_parent(path_text: str) -> Path:
    path = Path(path_text)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def draw_overlay(frame, line_y: int, counter: PeopleCounter, camera_name: str) -> None:
    _height, width = frame.shape[:2]
    cv2.line(frame, (0, line_y), (width, line_y), (0, 255, 255), 2)

    for track in counter.tracks.values():
        x, y = track.centroid
        box_x, box_y, box_w, box_h = track.box
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_w, box_y + box_h), (0, 200, 0), 2)
        cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)
        cv2.putText(
            frame,
            f"ID {track.track_id}",
            (box_x, max(20, box_y - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    stats = counter.stats
    cv2.rectangle(frame, (10, 10), (390, 140), (12, 18, 28), -1)
    cv2.putText(
        frame,
        f"Camera: {camera_name}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        f"Total entered: {stats.total_entered}",
        (20, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        f"Male count: {stats.male_count}",
        (20, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        f"Female count: {stats.female_count}",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )


def resize_frame(frame, target_width: int):
    height, width = frame.shape[:2]
    target_height = int(height * (target_width / width))
    return cv2.resize(frame, (target_width, target_height))


def process_frame(
    frame,
    counter: PeopleCounter,
    detector: YoloPersonDetector,
    event_logger: EntryEventLogger,
    csv_log_path: Optional[Path],
    camera_name: str,
) -> None:
    detections = detector.detect(frame)
    entry_events = counter.update(detections)

    for event in entry_events:
        event_logger.log_entry(event, camera_name=camera_name)
        if csv_log_path is not None:
            write_csv_row(csv_log_path, event, camera_name=camera_name)

    summary = event_logger.get_summary()
    counter.attach_gender_counts(
        male_count=summary["male_count"],
        female_count=summary["female_count"],
    )


def main() -> None:
    args = parse_args()
    capture = open_source(args.source)

    if not capture.isOpened():
        raise RuntimeError(f"Unable to open video source: {args.source}")

    database_path = ensure_parent(args.database)
    csv_log_path = ensure_parent(args.csv_log)

    counter: Optional[PeopleCounter] = None
    event_logger = EntryEventLogger(database_path)
    tracker_config = resolve_tracker_config(args.tracker, args.tracker_config)
    detector = YoloPersonDetector(
        model_path=args.model,
        confidence=args.confidence,
        tracker_config=tracker_config,
    )

    while True:
        success, frame = capture.read()
        if not success:
            break

        frame = resize_frame(frame, args.frame_width)

        if counter is None:
            line_y = int(frame.shape[0] * args.line_ratio)
            counter = PeopleCounter(
                line_y=line_y,
                max_missed_frames=args.max_missed_frames,
            )

        process_frame(
            frame=frame,
            counter=counter,
            detector=detector,
            event_logger=event_logger,
            csv_log_path=csv_log_path,
            camera_name=args.camera_name,
        )
        draw_overlay(frame, counter.line_y, counter, args.camera_name)
        cv2.imshow("Gate Entry Counter", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    event_logger.close()
    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
