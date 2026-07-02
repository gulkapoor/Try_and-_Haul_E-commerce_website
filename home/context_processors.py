from .models import Cart  # Import your Cart model

def cart_count(request):
    if request.user.is_authenticated:
        cart_items_count = Cart.objects.filter(cartUser=request.user).count()
    else:
        cart_items_count = 0  # Handle guest users if needed
    return {'cart_items_count': cart_items_count}
