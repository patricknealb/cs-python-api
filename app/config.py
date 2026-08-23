from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    supabase_url: str
    supabase_jwt_secret: str
    supabase_anon_key: str
    resend_api_key: str
    verify_base_url: str  # base URL of the API e.g. https://cs-python-api.onrender.com

    class Config:
        env_file = ".env"

settings = Settings()