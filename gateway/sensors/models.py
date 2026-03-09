from django.db import models
from django.utils import timezone


class Sensor(models.Model):
    name = models.CharField(
        'Имя датчика',
        max_length=100
    )
    unit = models.CharField(
        'Ед. изм.',
        max_length=20
    )
    on = models.BooleanField(
        'Включен',
        default=False
    )
    max_value = models.FloatField(
        'Максимальное значение',
        default=100
    )
    min_value = models.FloatField(
        'Минимальное значение',
        default=0
    )
    threshold_above = models.FloatField(
        'Верхний порог',
        null=True, blank=True
    )
    threshold_below = models.FloatField(
        'Нижний порог',
        null=True, blank=True
    )
    interval = models.IntegerField(
        'Интервал опроса',
        default=10
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.threshold_above is None:
            self.threshold_above = self.max_value
        if self.threshold_below is None:
            self.threshold_below = self.min_value
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name = 'Датчик'
        verbose_name_plural = 'Датчики'


class SensorData(models.Model):
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='data',
        verbose_name='Сенсор'
    )
    value = models.FloatField('Значение')
    timestamp = models.DateTimeField(
        'Время измерения',
        default=timezone.now
    )

    def __str__(self):
        return f'{self.sensor.name}, {self.timestamp}'

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['timestamp']
        verbose_name = 'Измерение'
        verbose_name_plural = 'Измерения'
