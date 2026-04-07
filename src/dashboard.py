from __future__ import annotations

import argparse
from pathlib import Path

from flask import Flask, jsonify, render_template

from storage import EntryEventLogger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dashboard for gate entry analytics.")
    parser.add_argument(
        "--database",
        default="data/gate_counter.db",
        help="SQLite database path used by the counter app.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface for the Flask dashboard.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port used by the Flask dashboard.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run Flask in debug mode.",
    )
    return parser.parse_args()


def create_app(database_path: str) -> Flask:
    app = Flask(__name__, template_folder="../templates")
    logger = EntryEventLogger(Path(database_path))

    @app.get("/")
    def index():
        return render_template("dashboard.html")

    @app.get("/api/summary")
    def summary():
        return jsonify(logger.get_summary())

    @app.get("/api/hourly")
    def hourly():
        return jsonify(logger.get_hourly_counts())

    @app.get("/api/recent-events")
    def recent_events():
        return jsonify(logger.get_recent_events())

    return app


def main() -> None:
    args = parse_args()
    app = create_app(args.database)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
