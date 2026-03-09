from dash import Input, Output, html, dcc
import plotly.graph_objs as go
from datetime import datetime
from django.utils import timezone
from sensors.models import SensorData


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


def init_tabs_callbacks(app):
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
            fig.update_layout(
                title='Изменение показаний во времени',
                xaxis_title='Время',
                yaxis_title=data[0].sensor.unit
            )
            return dcc.Graph(id='time-series-graph', figure=fig)

        elif tab == 'tab-hist':
            if not data:
                return dcc.Graph(id='hist-graph', figure=go.Figure())
            values = [d.value for d in data]
            fig = go.Figure(data=[go.Histogram(x=values, nbinsx=30)])
            fig.update_layout(
                title='Распределение значений',
                xaxis_title=data[0].sensor.unit,
                yaxis_title='Частота'
            )
            return dcc.Graph(id='hist-graph', figure=fig)

        return html.Div()
