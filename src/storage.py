from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Dict, List

from counter import EntryEvent


class EntryEventLogger:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.connection = sqlite3.connect(database_path)
        self.connection.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS entry_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER NOT NULL,
                crossed_at TEXT NOT NULL,
                direction TEXT NOT NULL,
                camera_name TEXT NOT NULL,
                centroid_x INTEGER NOT NULL,
                centroid_y INTEGER NOT NULL,
                box_x INTEGER NOT NULL,
                box_y INTEGER NOT NULL,
                box_w INTEGER NOT NULL,
                box_h INTEGER NOT NULL,
                gender_label TEXT,
                external_person_id TEXT
            )
            """
        )
        self.connection.commit()

    def log_entry(self, event: EntryEvent, camera_name: str) -> None:
        self.connection.execute(
            """
            INSERT INTO entry_events (
                track_id,
                crossed_at,
                direction,
                camera_name,
                centroid_x,
                centroid_y,
                box_x,
                box_y,
                box_w,
                box_h
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.track_id,
                event.crossed_at.isoformat(),
                event.direction,
                camera_name,
                event.centroid_x,
                event.centroid_y,
                event.box_x,
                event.box_y,
                event.box_w,
                event.box_h,
            ),
        )
        self.connection.commit()

    def attach_demographic_label(
        self,
        event_id: int,
        gender_label: str,
        external_person_id: str | None = None,
    ) -> None:
        self.connection.execute(
            """
            UPDATE entry_events
            SET gender_label = ?, external_person_id = ?
            WHERE id = ?
            """,
            (gender_label, external_person_id, event_id),
        )
        self.connection.commit()

    def get_summary(self) -> Dict[str, int]:
        query = """
            SELECT
                COUNT(*) AS total_entered,
                SUM(CASE WHEN gender_label = 'male' THEN 1 ELSE 0 END) AS male_count,
                SUM(CASE WHEN gender_label = 'female' THEN 1 ELSE 0 END) AS female_count
            FROM entry_events
            WHERE direction = 'in'
        """
        row = self.connection.execute(query).fetchone()
        return {
            "total_entered": int(row["total_entered"] or 0),
            "male_count": int(row["male_count"] or 0),
            "female_count": int(row["female_count"] or 0),
        }

    def get_hourly_counts(self, limit: int = 24) -> List[Dict[str, int | str]]:
        query = """
            SELECT
                strftime('%Y-%m-%d %H:00', crossed_at) AS hour_bucket,
                COUNT(*) AS total
            FROM entry_events
            WHERE direction = 'in'
            GROUP BY hour_bucket
            ORDER BY hour_bucket DESC
            LIMIT ?
        """
        rows = self.connection.execute(query, (limit,)).fetchall()
        return [
            {
                "hour_bucket": row["hour_bucket"],
                "total": int(row["total"]),
            }
            for row in reversed(rows)
        ]

    def get_recent_events(self, limit: int = 20) -> List[Dict[str, str | int | None]]:
        query = """
            SELECT
                id,
                crossed_at,
                camera_name,
                gender_label,
                external_person_id,
                track_id
            FROM entry_events
            ORDER BY crossed_at DESC
            LIMIT ?
        """
        rows = self.connection.execute(query, (limit,)).fetchall()
        return [
            {
                "id": int(row["id"]),
                "crossed_at": row["crossed_at"],
                "camera_name": row["camera_name"],
                "gender_label": row["gender_label"],
                "external_person_id": row["external_person_id"],
                "track_id": int(row["track_id"]),
            }
            for row in rows
        ]

    def close(self) -> None:
        self.connection.close()


def write_csv_row(csv_path: Path, event: EntryEvent, camera_name: str) -> None:
    file_exists = csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if not file_exists:
            writer.writerow(
                [
                    "track_id",
                    "crossed_at",
                    "direction",
                    "camera_name",
                    "centroid_x",
                    "centroid_y",
                    "box_x",
                    "box_y",
                    "box_w",
                    "box_h",
                ]
            )

        writer.writerow(
            [
                event.track_id,
                event.crossed_at.isoformat(),
                event.direction,
                camera_name,
                event.centroid_x,
                event.centroid_y,
                event.box_x,
                event.box_y,
                event.box_w,
                event.box_h,
            ]
        )
