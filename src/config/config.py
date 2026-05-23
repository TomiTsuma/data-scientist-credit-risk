from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Config:
    root_dir: Path = Path(__file__).resolve().parents[2]
    raw_data_dir: Path = root_dir / 'data' / 'raw'
    interim_dir: Path = root_dir / 'data' / 'interim'
    processed_dir: Path = root_dir / 'data' / 'processed'
    models_dir: Path = root_dir / 'models'
    artifacts_dir: Path = root_dir / 'artifacts'
    reports_dir: Path = root_dir / 'reports'

    @property
    def raw_data_file(self) -> Path:
        return self.raw_data_dir / 'Senior_Data_Scientist_Assessment_Data.xlsx'
