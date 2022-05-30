from django.db import models


class WeeklyReward(models.Model):

    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True)
    amount = models.FloatField(null=False, default=0.0)
    calculated = models.BooleanField(null=False, default=False)
    shared_total = models.FloatField(null=True, default=0.0)  # for just performance
    paid = models.BooleanField(null=False, default=False)
