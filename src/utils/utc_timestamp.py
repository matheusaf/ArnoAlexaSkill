# Datetime format for timeOfSample is ISO 8601, `YYYY-MM-DDThh:mm:ssZ`.

from datetime import datetime, timezone


def get_utc_timestamp(seconds=None, tz=timezone.utc):
    return datetime.now(tz).isoformat()
