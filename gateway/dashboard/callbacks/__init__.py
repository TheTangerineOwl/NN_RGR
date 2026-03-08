from .dropdown import init_dropdown_callbacks
from .tabs import init_tabs_callbacks
from .common import init_common_callbacks


def init_callbacks(app):
    """Инициализирует все callback'и, передавая им экземпляр app."""
    init_dropdown_callbacks(app)
    init_tabs_callbacks(app)
    init_common_callbacks(app)
