from django.db import models

from django.utils.translation import gettext_lazy as _
from django.contrib.messages import add_message, ERROR
from django.core.exceptions import ObjectDoesNotExist


class Configuration(models.Model):
    name = models.CharField(null=False, unique=True, max_length=32, verbose_name=_('Name'))
    value = models.CharField(null=True, max_length=128, verbose_name=_('Value'))
    # @todo create many to many thread connection to see active threads


    @staticmethod
    def is_trade_engine_active() -> bool:
        try:
            configuration = Configuration.objects.get(name='trade_engine_status')
            if configuration.value == "on":
                return True
            else:
                return False
        except ObjectDoesNotExist:
            #add_message(self.request, level=ERROR, message=_(f'User cannot access trade_engine_status.'), extra_tags='is-danger')
            pass
        return False

    @staticmethod
    def set_trade_engine_status(status):
        if status in ['on', 'off']:
            Configuration.objects.update_or_create(name='trade_engine_status', defaults={"value": status})

    @staticmethod
    def is_initialized() -> bool:
        try:
            configuration = Configuration.objects.get(name='initialization_status')
            if configuration.value == "yes":
                return True
            else:
                return False
        except ObjectDoesNotExist:
            #add_message(self.request, level=ERROR, message=_(f'User cannot access trade_engine_status.'), extra_tags='is-danger')
            pass
        return False

    @staticmethod
    def set_initialization_status(status):
        if status in ['yes', 'no']:
            Configuration.objects.update_or_create(name='initialization_status', defaults={"value": status})



