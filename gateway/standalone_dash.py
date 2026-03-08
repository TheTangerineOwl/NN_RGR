from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway.settings')
django.setup()

from dashboard.models import Sensor, SensorData

app = Dash(__name__)

app.layout = html.Div([
    html.H1("IoT Dashboard"),
    dcc.Dropdown(id='sensor-dropdown'),
    dcc.Graph(id='sensor-graph'),
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
])


@app.callback(
    Output('sensor-dropdown', 'options'),
    Output('sensor-dropdown', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_dropdown(n, **kwargs):   # добавляем **kwargs
    sensors = Sensor.objects.all()[:5]
    options = [{'label': s.name, 'value': s.id} for s in sensors]
    value = sensors[0].id if sensors else None
    return options, value


@app.callback(
    Output('sensor-graph', 'figure'),
    Input('sensor-dropdown', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_graph(sensor_id, n, **kwargs):   # добавляем **kwargs
    if not sensor_id:
        return go.Figure()
    data = SensorData.objects.filter(sensor_id=sensor_id)
    if data.count() == 0:
        return go.Figure()
    trace = go.Scatter(
        x=[d.timestamp.isoformat() for d in data],
        y=[d.value for d in data],
        mode='lines+markers'
    )
    return go.Figure(data=[trace])

if __name__ == '__main__':
    app.run(debug=True, port=8050)
