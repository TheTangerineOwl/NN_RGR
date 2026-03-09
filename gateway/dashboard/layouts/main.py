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

            html.Div([
                html.Label("Датчик:"),
                dcc.Dropdown(id='sensor-dropdown',
                             options=[],
                             value=None,
                             clearable=False)
            ], style={'marginRight': '20px', 'flex': '1'}),

            html.Div([
                html.Label("Период"),
                DashDatetimepicker(
                    id='datetime-picker',
                    startDate=start_str,
                    endDate=end_str,
                ),
            ], style={'marginRight': '20px'}),

            html.Div([
                html.Label("Состояние датчика:"),
                dcc.RadioItems(
                    id='sensor-switch',
                    options=[
                        {'label': 'Вкл', 'value': True},
                        {'label': 'Выкл', 'value': False}
                    ],
                    value=None,
                    labelStyle={'display': 'inline-block',
                                'marginRight': '10px'}
                )
            ], style={'flex': '0 0 auto'})
        ], style={'display': 'flex',
                  'flexDirection': 'row',
                  'alignItems':
                  'flex-end',
                  'margin': '20px',
                  'padding': '10px',
                  'border': '1px solid #ddd',
                  'borderRadius': '5px'}),

        html.Div([
            dcc.Graph(id='current-gauge'),
            html.Hr(),
            html.Label("Уведомлять, когда значение ниже:"),
            dcc.Slider(
                id='threshold-below-slider',
                min=0, max=100, value=20,
                step=1,
                marks={0: '0', 100: '100'},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            html.Br(),
            html.Label("Уведомлять, когда значение выше:"),
            dcc.Slider(
                id='threshold-above-slider',
                min=0, max=100, value=80,
                step=1,
                marks={0: '0', 100: '100'},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], id='thresholds-container', style={'display': 'none',
                                             'marginTop': 20,
                                             'padding': '10px',
                                             'border': '1px solid #ddd',
                                             'borderRadius': '5px'}),

        dcc.Tabs(id='tabs', value='tab-time', children=[
            dcc.Tab(label='Временной ряд', value='tab-time'),
            dcc.Tab(label='Гистограмма', value='tab-hist'),
        ]),
        html.Div(id='tab-content'),
        dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
    ])
