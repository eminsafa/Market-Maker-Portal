from django.db import models


class RewardCalculation(models.Model):

    pool = models.ForeignKey('liquidminers.Pool', on_delete=models.CASCADE, null=True)
    amount = models.FloatField(null=False, default=0.0)
    week = models.ForeignKey('liquidminers.Week', on_delete=models.CASCADE, null=True)
    duration = models.IntegerField(null=False, default=1)  # in minute
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
