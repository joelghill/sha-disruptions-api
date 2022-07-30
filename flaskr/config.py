import os

CACHE_TYPE = "SimpleCache" # Flask-Caching related configs
CACHE_DEFAULT_TIMEOUT = 300
SECRET = os.environ.get("SECRET_KEY", "dev")