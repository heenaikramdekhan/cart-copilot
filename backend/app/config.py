from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str
    supabase_url: str
    supabase_service_key: str

    # eBay Browse API OAuth client credentials. Optional so the app boots
    # without them; Product Search reports the store unavailable when absent.
    ebay_app_id: str = ""
    ebay_cert_id: str = ""

    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
