from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"

DATASET_FILES = {
    "application": DATA_DIR / "application_train.csv",
    "bureau": DATA_DIR / "bureau.csv",
}

CHART_COLORS = [
    "#087F8C",
    "#0563D6",
    "#14B8A6",
    "#F97316",
    "#A78BFA",
]
