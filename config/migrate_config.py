import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv()

from config.config_manager import save_config, load_config, default_config

def migrate():
    print("Uploading default config to S3...")
    config = default_config()
    save_config(config)
    print("Done! Verifying...")
    loaded = load_config()
    countries = list(loaded["countries"].keys())
    print(f"Config verified — countries: {countries}")

if __name__ == "__main__":
    migrate()