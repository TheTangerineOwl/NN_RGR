from dash import Input, Output, State, no_update
from sensors.models import Sensor


def init_sensor_control_callbacks(app):
    @app.callback(
        Output('sensor-switch', 'value'),
        Input('sensor-dropdown', 'value'),
        prevent_initial_call=True
    )
    def update_switch_on_sensor_change(dropdown_val, **kwargs):
        if dropdown_val is None:
            return no_update
        try:
            sensor = Sensor.objects.get(id=dropdown_val)
            return sensor.on
        except Sensor.DoesNotExist:
            return no_update

    @app.callback(
        Output('sensor-switch', 'value', allow_duplicate=True),
        Input('sensor-switch', 'value'),
        State('sensor-dropdown', 'value'),
        prevent_initial_call=True
    )
    def save_sensor_state(new_state, sensor_id, **kwargs):
        if sensor_id is not None and new_state is not None:
            Sensor.objects.filter(id=sensor_id).update(on=new_state)
        return no_update
