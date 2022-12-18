import json
import os
from os.path import join

_filename = os.getenv("BOT_CONFIG", "development") + ".json"
with open(join("config", _filename), encoding="utf-8") as f:
    config = json.load(f)

_token = config.get("TOKEN", "0:")
_bot_id, _ = _token.split(":")
config["BOT_ID"] = int(_bot_id)
