from django.shortcuts import HttpResponse

from liquidminers.integrations.exchange_factory import ExchangeFactory
from liquidminers.models.mixins import Status
from liquidminers.models.order import Order
from liquidminers.models.user import User


def api_cancel_order(request):
    keys = request.GET.keys()
    if 'order_eid' in keys and 'user_id' in keys and 'order_id' in keys:
        result = cancel_order(request.GET['user_id'], request.GET['order_eid'], request.GET['order_id'])
        return HttpResponse(result)
    else:
        return HttpResponse('{"error":false, "message":"Unauthorized!"}')


def cancel_order(user_id, order_eid, order_id):
    users = User.objects.filter(id=user_id)
    if len(users) == 1:
        user = users[0]
        orders = Order.objects.filter(id=order_id, eid=order_eid)
        if len(orders) == 1:
            order = orders[0]
            exchange = ExchangeFactory.get(user, order.investment.pool.pair.exchange)
            cancel_result = exchange.cancel_order(order)
            if cancel_result:
                order.status = Status.objects.get(name='CANCELLED')
                order.save()
                print('{"error":false, "message":"Order (' + str(order.eid) + ') cancelled successfully!"}')
                return '{"error":false, "message":"Order (' + str(order.eid) + ') cancelled successfully!"}'
            else:
                print( '{"error":true, "message":"Could not cancelled!"}')
                return '{"error":true, "message":"Could not cancelled!"}'
        else:
            print( '{"error":true, "message":"Order not found!"}')
            return '{"error":true, "message":"Order not found!"}'
    else:
        print('{"error":true, "message":"Unauthorized!"}')
        return '{"error":true, "message":"Unauthorized!"}'
