from django.core.management.base import BaseCommand
from django.utils import timezone

from liquidminers.integrations.threads.order_controller import OrderController


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        order_controller = OrderController('DEFAULT')
        order_controller.main()
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)
