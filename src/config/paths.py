from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / 'data' / 'raw'
DATA_INTERIM = ROOT / 'data' / 'interim'
DATA_PROCESSED = ROOT / 'data' / 'processed'
MODELS = ROOT / 'models'
ARTIFACTS = ROOT / 'artifacts'
REPORTS = ROOT / 'reports'
