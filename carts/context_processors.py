from .models import Cart,CartItem
from .views import __get_id

def Counter(request):
    cart_count=0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart=Cart.objects.filter(cart_id=__get_id(request)).first()
            cart_items=CartItem.objects.filter(cart=cart)
            for cart_item in cart_items:
                cart_count+=cart_item.quantity
        except Cart.DoesNotExist:
            cart_count=0
    return {'cart_count':cart_count}
            