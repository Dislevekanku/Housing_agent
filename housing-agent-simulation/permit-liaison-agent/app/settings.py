from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "permit-liaison-agent"
    SERVICE_VERSION: str = "0.1.0"
    
    class Config:
        env_file = ".env"

settings = Settings()
