from dash import Input, Output
from sensors.models import Sensor


def init_dropdown_callbacks(app):
    @app.callback(
        Output('sensor-dropdown', 'options'),
        Input('interval-component', 'n_intervals')
    )
    def update_sensor_list(n, **kwargs):
        sensors = Sensor.objects.all()
        return [{'label': s.name, 'value': s.id} for s in sensors]
