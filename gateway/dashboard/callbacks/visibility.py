from dash import Input, Output


def init_visibility_callbacks(app):
    @app.callback(
        Output('thresholds-container', 'style'),
        Input('sensor-dropdown', 'value')
    )
    def toggle_thresholds_visibility(sensor_id, **kwargs):
        if sensor_id is not None:
            return {'display': 'block', 'marginTop': 20, 'padding': '10px',
                    'border': '1px solid #ddd', 'borderRadius': '5px'}
        else:
            return {'display': 'none'}
