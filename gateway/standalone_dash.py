from dash import dcc, html, Dash
from dash.dependencies import Input, Output
from dash_datetimepicker import DashDatetimepicker
import plotly.graph_objs as go
from datetime import datetime, timedelta
from django import setup as dj_setup
from django.utils import timezone
from os import environ
from dotenv import load_dotenv
load_dotenv()
environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway.settings')
dj_setup()
from sensors.models import Sensor, SensorData


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


app = Dash(__name__)

end = datetime.now()
start = end - timedelta(hours=24)
start_str = start.strftime('%Y-%m-%dT%H:%M:%S')
end_str = end.strftime('%Y-%m-%dT%H:%M:%S')

app.layout = html.Div([
    html.H1("Умный дом - Дашборд"),

    html.Div([
            html.Label("Датчик:"),
            dcc.Dropdown(
                id='sensor-dropdown',
                options=[],
                value=None,
                clearable=False
            ),

            DashDatetimepicker(
                id='datetime-picker',
                startDate=start_str,
                endDate=end_str,
            ),
        ],
        style={'margin': 20}
    ),

    dcc.Tabs(id='tabs', value='tab-time', children=[
        dcc.Tab(label='Временной ряд', value='tab-time'),
        dcc.Tab(label='Гистограмма', value='tab-hist'),
        dcc.Tab(label='Текущие показания', value='tab-current'),
    ]),

    html.Div(id='tab-content'),

    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
])


@app.callback(
    Output('sensor-dropdown', 'options'),
    Input('interval-component', 'n_intervals')
)
def update_sensor_list(n, **kwargs):
    sensors = Sensor.objects.all()
    return [{'label': s.name, 'value': s.id} for s in sensors]


@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value'),
    Input('sensor-dropdown', 'value'),
    Input('datetime-picker', 'startDate'),
    Input('datetime-picker', 'endDate'),
    Input('interval-component', 'n_intervals')
)
def render_tab(tab, sensor_id, start_str, end_str, n, **kwargs):
    if not sensor_id:
        return html.Div("Выберите датчик")

    start_date = parse_datetime(start_str)
    end_date = parse_datetime(end_str) or timezone.now()

    queryset = SensorData.objects.filter(sensor_id=sensor_id)
    if start_date:
        queryset = queryset.filter(timestamp__gte=start_date)
    if end_date:
        queryset = queryset.filter(timestamp__lte=end_date)
    data = list(queryset)

    if tab == 'tab-time':
        if not data:
            return dcc.Graph(id='time-series-graph', figure=go.Figure())
        trace = go.Scatter(
            x=[d.timestamp for d in data],
            y=[d.value for d in data],
            mode='lines+markers'
        )
        fig = go.Figure(data=[trace])
        fig.update_layout(title='Изменение показаний во времени')
        return dcc.Graph(id='time-series-graph', figure=fig)

    elif tab == 'tab-hist':
        if not data:
            return dcc.Graph(id='hist-graph', figure=go.Figure())
        values = [d.value for d in data]
        fig = go.Figure(data=[go.Histogram(x=values, nbinsx=30)])
        fig.update_layout(title='Распределение значений')
        return dcc.Graph(id='hist-graph', figure=fig)

    elif tab == 'tab-current':
        if not data:
            return html.Div("Нет данных за выбранный период")
        latest = data[-1]
        data_sorted = sorted(data, key=lambda x: x.timestamp)
        latest = data_sorted[-1]

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=latest.value,
            title={
                'text': f"Последнее значение ({
                    latest.timestamp.strftime('%Y-%m-%d %H:%M')
                })"
            },
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 100], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }))
        fig.update_layout(height=300)
        return dcc.Graph(id='current-gauge', figure=fig)

    return html.Div()


if __name__ == '__main__':
    app.run(debug=True, port=8050)
