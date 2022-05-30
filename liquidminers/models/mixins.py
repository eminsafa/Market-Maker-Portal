from django.db import models

from django.utils.translation import gettext_lazy as _


class Status(models.Model):

    name = models.CharField(null=False, unique=True, max_length=32, verbose_name=_('Name'))
    style = models.CharField(null=True, max_length=64, verbose_name=_('Style'))


class Week(models.Model):

    start = models.DateTimeField(null=True, verbose_name=_('Beginning of Week'))
    end = models.DateTimeField(null=True, verbose_name=_('End of Week'))

    @staticmethod
    def get(dt):
        return Week.objects.get(start__lte=dt, end__gte=dt)

