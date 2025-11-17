from pydantic_settings import BaseSettings

from pathlib import Path
from typing import Dict

class Settings(BaseSettings):
    SERVICE_NAME: str = "data-scout-agent"
    SERVICE_VERSION: str = "0.1.0"
    # path to CSV/Parquet/DB conn - prefer fixtures if available
    PARCELS_PATH: str = str(Path(__file__).parent.parent / "fixtures" / "parcels.csv")
    MAX_RESULTS: int = 25
    DEFAULT_MIN_VACANCY: float = 0.0
    DEFAULT_MIN_TRANSIT: float = 0.0
    SCORE_WEIGHTS: Dict[str, float] = {
        "vacancy": 0.5,
        "transit": 0.3,
        "lot_sqft": 0.2,
    }

    class Config:
        env_file = ".env"

settings = Settings()
