# Gate Entry People Counter

This project counts how many people enter through a company gate from a video or camera feed and stores those entry events for reporting.

It now includes:

- YOLO-based person detection
- Selectable ByteTrack or BoT-SORT tracking through YOLO
- SQLite event logging for persistent analytics
- CSV logging for exports and audits
- A small Flask dashboard for totals, hourly activity, and recent events

## Important note about male/female counting

Automatically inferring "male" and "female" from camera appearance is sensitive and often unreliable. It can create accuracy, privacy, and fairness problems.

Recommended approach:

- Use the camera model only to count total human entries
- If you truly need a male/female breakdown, join the entry event with another trusted business source such as employee records, visitor registration, or badge data

This project therefore implements:

- `total_entered` from the camera
- Optional `male_count` and `female_count` fields attached from non-vision sources

## Project structure

```text
src/
  app.py
  counter.py
  dashboard.py
  detector.py
  storage.py
templates/
  dashboard.html
requirements.txt
README.md
```

## Setup

1. Create a virtual environment
2. Install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run the counter with webcam

```powershell
python src/app.py
```

On first run, the `ultralytics` package may download the YOLO model weights if they are not already cached on your machine.

## Run the counter with a video file

```powershell
python src/app.py --source path\to\gate_video.mp4
```

## Run the dashboard

```powershell
python src/dashboard.py
```

Then open `http://127.0.0.1:5000`.

## Data files

By default the app creates:

- `data/gate_counter.db`
- `data/entry_events.csv`

You can change those paths with `--database` and `--csv-log`.

## Controls

- `q`: quit

## How the counter works

1. YOLO detects only the `person` class in each frame
2. ByteTrack or BoT-SORT keeps a stable tracker ID for each detected person
3. A horizontal virtual line marks the entry zone
4. A person is counted once when their tracked center crosses that line in the configured direction
5. Each crossing creates a record in SQLite and CSV
6. The dashboard reads analytics directly from SQLite

## Recommended production upgrade path

For a real company deployment, I recommend upgrading this prototype to:

- A stronger tracker such as ByteTrack or DeepSORT
- One-way gate geometry calibration
- Role-based access to analytics
- Privacy and compliance review before deployment
- Multiple cameras with a shared event store
- Health checks and alerting for camera/model failures

## Example business-safe gender workflow

Instead of predicting gender from appearance:

1. Count the person at the gate camera
2. Store an entry event with timestamp and track ID
3. Match that event with a badge swipe or visitor registration
4. Read demographic fields only from the authorized business record if your policy permits it

That gives you a much safer design than camera-based gender guessing.

## Useful options

```powershell
python src/app.py --source 0 --model yolov8n.pt --camera-name gate_a
python src/app.py --source recordings\gate.mp4 --line-ratio 0.55 --confidence 0.4
python src/app.py --source 0 --tracker bytetrack
python src/app.py --source 0 --tracker botsort
python src/app.py --source 0 --tracker-config custom_tracker.yaml
python src/dashboard.py --database data/gate_counter.db --port 5050
```

## Voice gender recognition project

This repository now also includes a standalone end-to-end machine learning project for gender recognition using voice.

### Files

```text
app.py
model.py
utils.py
templates/
  index.html
artifacts/
uploads/
```

### Dataset options

- `data/voice.csv`
- A labeled audio directory such as:

```text
data/audio/
  male/
    sample_1.wav
  female/
    sample_2.wav
```

### Train the model

```powershell
python model.py --data data/voice.csv
```

The training script:

- loads data with pandas
- handles missing values
- encodes labels as `male=1`, `female=0`
- trains Logistic Regression, Random Forest, and SVM
- compares test accuracy and cross-validation scores
- tunes the best candidates with `GridSearchCV`
- saves the best model to `artifacts/models/best_gender_model.joblib`
- saves reports to `artifacts/reports/`

### Run the Flask app

```powershell
python app.py
```

Then open `http://127.0.0.1:5000` and upload a `.wav` file to see the predicted gender.
