import random
import math
import time
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from sensors.models import Sensor, SensorData


class TemperatureGenerator:
    """Генератор температуры с суточным циклом и инерцией"""
    def __init__(self, base_temp=22.0, daily_amplitude=3.0, phase=4.0,
                 noise_sigma=0.2, inertia=0.95):
        """
        base_temp: средняя температура за сутки
        daily_amplitude: амплитуда суточных колебаний
        phase: час минимальной температуры (0-23), например 4 утра
        noise_sigma: стандартное отклонение случайного шума
        inertia: коэффициент инерции (0..1)
        """
        self.base_temp = base_temp
        self.daily_amplitude = daily_amplitude
        self.phase = phase
        self.noise_sigma = noise_sigma
        self.inertia = inertia
        self.prev_value = None

    def target_temp(self, t):
        """Целевая температура в момент времени t (datetime)"""
        hour = t.hour + t.minute/60.0 + t.second/3600.0
        daily = self.daily_amplitude * math.cos(
            2 * math.pi * (hour - self.phase) / 24.0
        )
        return self.base_temp + daily

    def next_value(self, current_time):
        """Генерирует следующее значение температуры"""
        target = self.target_temp(current_time)
        if self.prev_value is None:
            value = target + random.gauss(0, self.noise_sigma)
        else:
            diff = target - self.prev_value
            value = self.prev_value + self.inertia * diff + random.gauss(
                0, self.noise_sigma
            )
        self.prev_value = value
        return value


class Command(BaseCommand):
    help = 'Генерирует реалистичные тестовые данные температуры для датчиков'

    def add_arguments(self, parser):
        parser.add_argument('--sensors', nargs='+', type=int,
                            help='ID датчиков (если не указаны, берутся все)')
        # parser.add_argument('--interval', type=int, default=30,
        #                     help='Интервал в секундах')
        parser.add_argument('--hours', type=int, default=None,
                            help='Заполнить историю за последние N часов')

        parser.add_argument('--base-temp', type=float, default=22.0,
                            help='Средняя температура')
        parser.add_argument('--daily-amplitude', type=float, default=3.0,
                            help='Суточная амплитуда')
        parser.add_argument('--phase', type=float, default=4.0,
                            help='Час минимальной температуры (0-23)')
        parser.add_argument('--noise-sigma', type=float, default=0.2,
                            help='Стандартное отклонение шума')
        parser.add_argument('--inertia', type=float, default=0.95,
                            help='Коэффициент инерции (0-1)')

    def handle(self, *args, **options):
        # interval = options['interval']
        hours = options['hours']
        sensor_ids = options['sensors']

        base_temp = options['base_temp']
        daily_amplitude = options['daily_amplitude']
        phase = options['phase']
        noise_sigma = options['noise_sigma']
        inertia = options['inertia']

        if sensor_ids:
            sensors = Sensor.objects.filter(id__in=sensor_ids)
        else:
            sensors = Sensor.objects.all()

        if not sensors.exists():
            self.stderr.write('Нет датчиков для генерации')
            return

        generators = {}
        for s in sensors:
            generators[s.id] = TemperatureGenerator(
                base_temp=base_temp,
                daily_amplitude=daily_amplitude,
                phase=phase,
                noise_sigma=noise_sigma,
                inertia=inertia
            )

        self.stdout.write(
            f'Генерация для {sensors.count()} датчиков'
        )

        if hours:
            end = timezone.now()
            start = end - timedelta(hours=hours)
            # current = start
            self.stdout.write('Заполнение истории...')
            count = 0
            for s in sensors:
                current = start
                gen = generators[s.id]
                while current <= end:
                    val = gen.next_value(current)
                    if val > s.max_value:
                        val = s.max_value
                    if val < s.min_value:
                        val = s.min_value
                    SensorData.objects.create(
                        sensor=s,
                        value=val,
                        timestamp=current
                    )
                    count += 1
                    current += timedelta(seconds=s.interval)
            self.stdout.write(f'История заполнена: {count} записей.')

        self.stdout.write(
            'Запуск генерации в реальном времени. Для остановки Ctrl+C'
        )
        try:
            wait_till = {}
            step = sensors[0].interval
            for s in sensors:
                wait_till[s] = s.interval
                step = min(step, s.interval)
            while True:
                now = timezone.now()
                for s in sensors:
                    wait_till[s] -= step
                    if wait_till[s] > 0:
                        continue
                    gen = generators[s.id]
                    val = gen.next_value(now)
                    if val > s.max_value:
                        val = s.max_value
                    if val < s.min_value:
                        val = s.min_value
                    SensorData.objects.create(
                        sensor=s,
                        value=val,
                        timestamp=now
                    )
                    wait_till[s] = s.interval
                    self.stdout.write(
                        f'{now.strftime("%Y-%m-%d %H:%M:%S")}: '
                        f'+ запись сенсора {s}, показание {val:.2f}'
                    )
                time.sleep(step)
        except KeyboardInterrupt:
            self.stdout.write('Остановлено.')
