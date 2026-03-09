from dash import Input, Output, State, no_update
import plotly.graph_objs as go
from sensors.models import Sensor, SensorData


def init_thresholds_callbacks(app):
    @app.callback(
        Output('threshold-below-slider', 'min'),
        Output('threshold-below-slider', 'max'),
        Output('threshold-below-slider', 'value'),
        Output('threshold-above-slider', 'min'),
        Output('threshold-above-slider', 'max'),
        Output('threshold-above-slider', 'value'),
        Input('sensor-dropdown', 'value'),
    )
    def update_sliders_from_sensor(sensor_id, **kwargs):
        if sensor_id is None:
            return (no_update,) * 6
        try:
            sensor = Sensor.objects.get(id=sensor_id)
            return (sensor.min_value, sensor.max_value, sensor.threshold_below,
                    sensor.min_value, sensor.max_value, sensor.threshold_above)
        except Sensor.DoesNotExist:
            return (no_update,) * 6

    @app.callback(
        Output('current-gauge', 'figure'),
        Input('threshold-below-slider', 'value'),
        Input('threshold-above-slider', 'value'),
        Input('interval-component', 'n_intervals'),
        State('sensor-dropdown', 'value'),
    )
    def update_indicator(thr_bw, thr_ab, n, sensor_id, **kwargs):
        if sensor_id is None:
            return go.Figure()
        try:
            latest = SensorData.objects.filter(
                sensor_id=sensor_id
            ).latest('timestamp')
        except SensorData.DoesNotExist:
            return go.Figure()
        sensor = latest.sensor
        min_val = sensor.min_value
        max_val = sensor.max_value

        if latest.value <= thr_bw:
            bar_color = 'blue'
        elif latest.value >= thr_ab:
            bar_color = 'red'
        else:
            bar_color = 'green'

        step_width = (max_val - min_val) * 0.005
        thr_bw_low = max(thr_bw - step_width, min_val)
        thr_bw_high = min(thr_bw + step_width, max_val)
        thr_ab_low = max(thr_ab - step_width, min_val)
        thr_ab_high = min(thr_ab + step_width, max_val)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest.value,
            title={'text': f"Последнее значение ({
                latest.timestamp.strftime('%Y-%m-%d %H:%M')
            })"},
            number={'suffix': f" {sensor.unit}"},
            gauge={
                'axis': {'range': [min_val, max_val]},
                'bar': {'color': bar_color},
                'steps': [
                    {'range': [min_val, thr_bw_low], 'color': 'gray'},
                    {'range': [thr_bw_low, thr_bw_high], 'color': 'red'},
                    {'range': [thr_bw_high, thr_ab_low], 'color': 'lightgray'},
                    {'range': [thr_ab_low, thr_ab_high], 'color': 'red'},
                    {'range': [thr_ab_high, max_val], 'color': 'gray'},
                ],
            }
        ))
        fig.update_layout(height=300)
        return fig

    @app.callback(
        Output('threshold-below-slider', 'value', allow_duplicate=True),
        Input('threshold-below-slider', 'value'),
        Input('threshold-above-slider', 'value'),
        State('sensor-dropdown', 'value'),
        prevent_initial_call=True
    )
    def save_thresholds(thr_bw, thr_ab, sensor_id, **kwargs):
        if sensor_id is not None and thr_bw is not None and thr_ab is not None:
            Sensor.objects.filter(id=sensor_id).update(
                threshold_below=thr_bw,
                threshold_above=thr_ab
            )
        return no_update
