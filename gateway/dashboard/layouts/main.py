from dash import dcc, html
from dash_datetimepicker import DashDatetimepicker
from datetime import datetime, timedelta


def create_layout():
    """Возвращает основной layout приложения."""
    end = datetime.now()
    start = end - timedelta(hours=24)
    start_str = start.strftime('%Y-%m-%dT%H:%M:%S')
    end_str = end.strftime('%Y-%m-%dT%H:%M:%S')
    return html.Div([
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
