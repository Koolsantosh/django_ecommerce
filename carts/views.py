from django.shortcuts import render,redirect,HttpResponse
from store.models import Product,Variation
from carts.models import Cart,CartItem
from django.shortcuts import get_object_or_404

# Create your views here.

#this function will get the session key from the browser or create a session, if it was not created already: _ represent private function
def __get_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # Fetch the product by ID
    product_variation = []  # List to store selected variations
    
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            
            try:
                # Fetch the variation based on category and value
                variation = Variation.objects.get(
                    product=product, variation_category__iexact=key, variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass  # Ignore if variation does not exist
    
    # Retrieve or create a cart for the session
    try:
        cart = Cart.objects.get(cart_id=__get_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=__get_id(request))
        cart.save()
    
    # Check if the product already exists in the cart
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    
    if is_cart_item_exists:
        cart_items = CartItem.objects.filter(product=product, cart=cart)
        ex_var_list = []  # List to store existing variations
        id_list = []  # List to store cart item IDs
        
        for item in cart_items:
            existing_variation = item.variations.all()  # Fetch variations of each cart item
            ex_var_list.append(list(existing_variation))
            id_list.append(item.id)  # Store cart item IDs
        
        if product_variation in ex_var_list:
            # If the same variation exists, increase the quantity
            index = ex_var_list.index(product_variation)
            item_id = id_list[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            # If variation is different, create a new cart item
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if product_variation:
                item.variations.add(*product_variation)  # Add variations correctly
            item.save()
    else:
        # If cart item does not exist, create a new cart item
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if product_variation:
            cart_item.variations.add(*product_variation)  # Add variations
        cart_item.save()
    
    return redirect('cart')  # Redirect to cart page

def remove_cart(request,product_id,cart_item_id): #function will receive product_id in which - button is clicked
    cart=Cart.objects.get(cart_id=__get_id(request)) #accessing the cart first based on session_id
    product = get_object_or_404(Product,id=product_id) # access the product: to access the same product/cart_item of the cart
    try:
        cart_item=CartItem.objects.get(cart=cart,product=product,id=cart_item_id) #accessing the cart_item/product of the cart
        if cart_item.quantity > 1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    cart=Cart.objects.get(cart_id=__get_id(request))
    product=Product.objects.get(id=product_id)
    cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request,total=0,quantity=0,cart_items=None):
    tax=0
    grand_total=0
    try:
        cart=Cart.objects.get(cart_id=__get_id(request))
        cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total+=(cart_item.quantity * cart_item.product.price)
            quantity+=cart_item.quantity
        tax=(total*2)/100
        grand_total =total+tax

    except Cart.DoesNotExist or CartItem.DoesNotExist:
        pass
    
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
    }
    return render(request,'carts/cart.html',context)