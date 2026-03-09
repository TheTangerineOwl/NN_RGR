from dash import html
from django.db import models
from django.utils import timezone
from datetime import timedelta
from sensors.models import Sensor, SensorData


def render_stats(sensor_id, start_date, end_date, **kwargs):
    try:
        sensor = Sensor.objects.get(id=sensor_id)
    except Sensor.DoesNotExist:
        return html.Div("Датчик не найден")

    qs = SensorData.objects.filter(sensor_id=sensor_id)

    total_count = qs.count()
    now = timezone.now()

    periods = {
        '1 час': now - timedelta(hours=1),
        '24 часа': now - timedelta(days=1),
        '1 неделя': now - timedelta(weeks=1),
        '1 месяц': now - timedelta(days=30),
    }
    period_counts = {}
    for label, since in periods.items():
        period_counts[label] = qs.filter(timestamp__gte=since).count()

    selected_count = None
    if start_date:
        selected_count = qs.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).count()

    day_ago = now - timedelta(days=1)
    stats_day = qs.filter(timestamp__gte=day_ago).aggregate(
        min_val=models.Min('value'),
        max_val=models.Max('value'),
        avg_val=models.Avg('value')
    )
    min_day_obj = qs.filter(
        timestamp__gte=day_ago,
        value=stats_day['min_val']
    ).first()
    max_day_obj = qs.filter(
        timestamp__gte=day_ago,
        value=stats_day['max_val']
    ).first()

    if start_date:
        stats_selected = qs.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).aggregate(
            min_val=models.Min('value'),
            max_val=models.Max('value'),
            avg_val=models.Avg('value')
        )
        min_sel_obj = qs.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date,
            value=stats_selected['min_val']
        ).first()
        max_sel_obj = qs.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date,
            value=stats_selected['max_val']
        ).first()
    else:
        stats_selected = {'min_val': None, 'max_val': None, 'avg_val': None}
        min_sel_obj = max_sel_obj = None

    def format_value_with_time(value, obj):
        if value is None or obj is None:
            return "—"
        return f"{value:.2f} ({obj.timestamp.strftime('%Y-%m-%d %H:%M')})"

    left_items = [
        ("Всего измерений", str(total_count)),
        ("Измерений за 1 час", str(period_counts.get('1 час', 0))),
        ("Измерений за 24 часа", str(period_counts.get('24 часа', 0))),
        ("Измерений за 1 неделя", str(period_counts.get('1 неделя', 0))),
        ("Измерений за 1 месяц", str(period_counts.get('1 месяц', 0))),
    ]
    left_items.append((
        "Измерений за выбранный период",
        str(selected_count) if selected_count is not None else "—"
    ))

    right_items = [
        ("Минимум за сутки", format_value_with_time(
            stats_day['min_val'],
            min_day_obj
        )),
        ("Максимум за сутки", format_value_with_time(
            stats_day['max_val'],
            max_day_obj
        )),
        ("Среднее за сутки", f"{stats_day['avg_val']:.2f}"
         if stats_day['avg_val']
         else "—"),
    ]
    if start_date:
        right_items.append(("Минимум за выбранный период",
                            format_value_with_time(
                                stats_selected['min_val'], min_sel_obj
                            )))
        right_items.append(("Максимум за выбранный период",
                            format_value_with_time(
                                stats_selected['max_val'], max_sel_obj
                            )))
        right_items.append(("Среднее за выбранный период",
                            f"{stats_selected['avg_val']:.2f}"
                            if stats_selected['avg_val']
                            else "—"))
    else:
        right_items.append(("Минимум за выбранный период", "—"))
        right_items.append(("Максимум за выбранный период", "—"))
        right_items.append(("Среднее за выбранный период", "—"))

    table_style = {
        'width': '100%',
        'borderCollapse': 'collapse',
        'marginTop': '20px',
        'fontFamily': 'Arial, sans-serif',
        'fontSize': '14px'
    }
    cell_style = {
        'padding': '4px 8px',
        'textAlign': 'left',
        'borderBottom': '1px solid #ddd'
    }

    rows = []
    for (
        left_label, left_value
        ), (
            right_label, right_value
            ) in zip(left_items, right_items):
        rows.append(html.Tr([
            html.Td(left_label, style=cell_style),
            html.Td(left_value, style=cell_style),
            html.Td(right_label, style=cell_style),
            html.Td(right_value, style=cell_style)
        ]))

    table = html.Table([
        html.Thead(html.Tr([
            html.Th("Показатель", style=cell_style),
            html.Th("Значение", style=cell_style),
            html.Th("Показатель", style=cell_style),
            html.Th("Значение", style=cell_style)
        ])),
        html.Tbody(rows)
    ], style=table_style)

    return html.Div([
        html.H3(f"Статистика по датчику: {sensor.name}"),
        table
    ])
