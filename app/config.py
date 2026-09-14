from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HACKRX_SECRET_TOKEN: str

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
