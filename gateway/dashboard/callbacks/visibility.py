from dash import Input, Output


def init_visibility_callbacks(app):
    @app.callback(
        Output('thresholds-container', 'style'),
        Input('sensor-dropdown', 'value')
    )
    def toggle_thresholds_visibility(sensor_id, **kwargs):
        if sensor_id is not None:
            return {'display': 'flex'}
        else:
            return {'display': 'none'}
