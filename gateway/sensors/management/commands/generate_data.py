import random
import time
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from sensors.models import Sensor, SensorData


class Command(BaseCommand):
    help = 'Генерирует тестовые данные для датчиков каждые N секунд'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sensors',
            nargs='+',
            type=int,
            help='ID датчиков (если не указаны, берутся все)'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Интервал в секундах'
        )
        parser.add_argument(
            '--min',
            type=float,
            default=20.0,
            help='Минимальное значение'
        )
        parser.add_argument(
            '--max',
            type=float,
            default=30.0,
            help='Максимальное значение'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=None,
            help='Заполнить историю за последние N часов'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        min_val = options['min']
        max_val = options['max']
        av = (max_val + min_val) / 2
        sensor_ids = options['sensors']
        hours = options['hours']

        if sensor_ids:
            sensors = Sensor.objects.filter(id__in=sensor_ids)
        else:
            sensors = Sensor.objects.all()

        if not sensors.exists():
            self.stderr.write('Нет датчиков для генерации')
            return

        self.stdout.write(
            f'Генерация для {
                sensors.count()
            } датчиков, интервал {interval} сек.'
        )

        last = {}
        for s in sensors:
            dat = SensorData.objects.filter(
                sensor=s).order_by('-timestamp').first()
            last[s] = dat.value if isinstance(dat, SensorData) else av

        if hours:
            end = timezone.now()
            start = end - timedelta(hours=hours)
            current = start
            self.stdout.write('Заполнение истории...')
            while current <= end:
                for s in sensors:
                    last[s] = SensorData.objects.create(
                        sensor=s,
                        # value=random.uniform(min_val, max_val),
                        value=random.normalvariate(mu=last[s]),
                        timestamp=current
                    ).value
                current += timedelta(seconds=interval)
            self.stdout.write('История заполнена.')

        self.stdout.write(
            'Запуск генерации в реальном времени. Для остановки Ctrl+C'
        )
        try:
            while True:
                now = timezone.now()
                for s in sensors:
                    last[s] = SensorData.objects.create(
                        sensor=s,
                        # value=random.uniform(min_val, max_val),
                        value=random.normalvariate(mu=last[s]),
                        timestamp=now
                    ).value
                self.stdout.write(
                    f'{
                        now.strftime("%Y-%m-%d %H:%M:%S")
                    }: +{sensors.count()} записей'
                )
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write('Остановлено.')
