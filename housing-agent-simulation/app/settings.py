from pydantic_settings import BaseSettings

from pathlib import Path

class Settings(BaseSettings):
    SERVICE_NAME: str = "data-scout-agent"
    SERVICE_VERSION: str = "0.1.0"
    # path to CSV/Parquet/DB conn - prefer fixtures if available
    PARCELS_PATH: str = str(Path(__file__).parent.parent / "fixtures" / "parcels.csv")
    MAX_RESULTS: int = 25

    class Config:
        env_file = ".env"

settings = Settings()
