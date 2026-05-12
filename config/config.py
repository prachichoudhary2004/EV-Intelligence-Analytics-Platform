import os
from pathlib import Path
from dotenv import load_dotenv

# Load env vars from .env file
load_dotenv()

class Config:
    """
    Holds all app settings and paths.
    """
    # Project Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    BRONZE_DIR = DATA_DIR / "bronze"
    SILVER_DIR = DATA_DIR / "silver"
    GOLD_DIR = DATA_DIR / "gold"
    MODEL_DIR = BASE_DIR / "models"
    FEATURE_STORE_DIR = BASE_DIR / "feature_store"
    ASSETS_DIR = BASE_DIR / "assets"
    
    # App Settings
    APP_NAME = "Enterprise EV Market Intelligence Platform"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Data Settings
    RAW_SALES_FILE = BRONZE_DIR / "ev_sales_data.csv"
    RAW_CHARGING_FILE = BRONZE_DIR / "charging_stations.csv"
    RAW_MARKET_FILE = BRONZE_DIR / "market_metrics.csv"
    
    # ML Settings
    RANDOM_STATE = 42
    TEST_SIZE = 0.2
    
    # UI Settings
    THEME_COLOR = "#00FF41"
    SECONDARY_COLOR = "#FF6B6B"
    BACKGROUND_COLOR = "#0E1117"
    CARD_COLOR = "#1E2139"
    
    @classmethod
    def ensure_dirs(cls):
        """Create folders if they don't exist."""
        for attr in dir(cls):
            if attr.endswith("_DIR"):
                path = getattr(cls, attr)
                if isinstance(path, Path):
                    path.mkdir(parents=True, exist_ok=True)

# Easy access to config
config = Config()
if __name__ == "__main__":
    config.ensure_dirs()
    print(f"Project Directories Initialized at {config.BASE_DIR}")
