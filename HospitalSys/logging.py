import environ

from pathlib import Path
from django.conf import settings



BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "handlers": {
        "file": {
            "level": env("DJANGO_LOG_LEVEL"),
            "filename": env("DJANGO_LOG_FILE"),
            "class": "logging.FileHandler",
            "formatter": "verbose"
        },
        "console": {
            "level": env("DJANGO_LOG_LEVEL"),
            "class": "logging.StreamHandler",
            "formatter": "simple"
        },
    },

    "loggers": {
        "": {
            "handlers": ["file", "console"],
            "level": env("DJANGO_LOG_LEVEL"),
        },
    },

    "formatters": {
        "simple": {
            "format": "{levelname}:{asctime}--{message}",
            "style": "{"
        },
        "verbose": {
            "format": "{levelname}:{asctime}:{name}:{module}.py:{funcName}():line~{lineno:d}:{message}",
            "style": "{"
        }
    }
}