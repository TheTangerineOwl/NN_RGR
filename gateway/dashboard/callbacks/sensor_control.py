from dash import Input, Output, State, callback, no_update
from sensors.models import Sensor


def init_sensor_control_callbacks(app):
    @app.callback(
        Output('sensor-switch', 'value'),
        Input('sensor-switch', 'value'),
        State('sensor-dropdown', 'value'),
        prevent_initial_call=True
    )
    def save_sensor_state(new_state, sensor_id, **kwargs):
        """Сохраняет состояние переключателя в БД."""
        if sensor_id is not None and new_state is not None:
            Sensor.objects.filter(id=sensor_id).update(on=new_state)
        return no_update
