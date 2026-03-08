# from django.db import models


# class Sensor(models.Model):
#     name = models.CharField(max_length=100)
#     unit = models.CharField(max_length=20)

#     def __str__(self):
#         return self.name


# class SensorData(models.Model):
#     sensor = models.ForeignKey(
#         Sensor,
#         on_delete=models.CASCADE,
#         related_name='data'
#     )
#     value = models.FloatField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'{self.sensor.name}, {self.timestamp}'
