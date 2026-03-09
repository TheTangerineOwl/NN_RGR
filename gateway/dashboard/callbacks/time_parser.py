from datetime import datetime
from django.utils import timezone


def parse_datetime(dt_str):
    """Преобразует строку от datetime-picker в aware datetime (UTC)."""
    if not dt_str:
        return None
    dt_str = dt_str.replace('Z', '+00:00')
    dt = datetime.fromisoformat(dt_str)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.UTC)
    else:
        dt = dt.astimezone(timezone.UTC)
    return dt
