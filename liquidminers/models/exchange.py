from django.db import models

from django.utils.translation import gettext_lazy as _

from liquidminers.models.mixins import Status


# @todo THIS CLASS HAS NOT IMPLEMENTED!
class Exchange(models.Model):

    name = models.CharField(max_length=32, null=False, default='<PAIR>', verbose_name=_('Name'))
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name=_('Status'))

