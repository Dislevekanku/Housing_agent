from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    SERVICE_NAME: str = "compliance-agent"
    SERVICE_VERSION: str = "0.1.0"
    ZONING_RULES_PATH: str = str(Path(__file__).parent.parent.parent / "fixtures" / "zoning_rules.json")
    CODE_POLICIES_PATH: str = str(Path(__file__).parent.parent.parent / "fixtures" / "code_policies.json")
    
    class Config:
        env_file = ".env"

settings = Settings()
