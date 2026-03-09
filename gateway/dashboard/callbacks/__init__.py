from .dropdown import init_dropdown_callbacks
from .tabs import init_tabs_callbacks
from .common import init_common_callbacks
from .sensor_control import init_sensor_control_callbacks
from .thresholds import init_thresholds_callbacks
from .visibility import init_visibility_callbacks


def init_callbacks(app):
    """Инициализирует все callback'и, передавая им экземпляр app."""
    init_dropdown_callbacks(app)
    init_tabs_callbacks(app)
    init_common_callbacks(app)
    init_sensor_control_callbacks(app)
    init_visibility_callbacks(app)
    init_thresholds_callbacks(app)
