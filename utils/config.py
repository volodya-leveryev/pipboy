import json
import os

env = "" if os.getenv("BOT_ENV") == "PRODUCTION" else "_dev"
with open(f"config{env}.json", encoding="utf-8") as f:
    config = json.load(f)
