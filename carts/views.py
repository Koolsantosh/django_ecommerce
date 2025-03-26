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


def add_cart(request,product_id):
    product=Product.objects.get(id=product_id) #get the product while adding to the cart, then fetching variation related to this product
    product_variation=[] #creating empty list to store variation of the product
    if request.method=='POST':
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                print(variation)
                product_variation.append(variation) #i think not necessary to use product_variation list, we can directly use variation
            except:
                pass
    
    try:
        cart=Cart.objects.get(cart_id=__get_id(request)) #get the cart based on cart_id present in the session key
    except Cart.DoesNotExist:
        # creating cart if not exist
        cart=Cart.objects.create(
            cart_id=__get_id(request)
            ) 
        cart.save() # saving cart
    # till here just cart is created, and we have/got product too, now need to create cart_items inside the cart

    is_cart_item_exists=CartItem.objects.filter(product=product,cart=cart).exists() #checking if the product is already exist in the cart_item or not   
    
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product,cart=cart) 
        #if product is already exist in the cart_item, we are increasing quantity by 1, if user press add to cart in product_detail page
        # existing variations -> database 
        # current variation -> product_variation list
        # item_id -> database

        ex_var_list=[]
        id=[]
        for item in cart_item:
            existing_variation = item.variations.all() #what is this .all() method?
            ex_var_list.append(list(existing_variation))
            id.append(item.id)
        print(ex_var_list)

        if product_variation in ex_var_list:
            # return HttpResponse('true')
            # increase the cart_item qunatity
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item=CartItem.objects.get(product=product,id=item_id)
            item.quantity+=1
            item.save()
        
        else: 
            item=CartItem.objects.create(product=product,quantity=1,cart=cart,)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)

            item.save()

    else:
        cart_item=CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
       
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        
        cart_item.save()

    return redirect('cart')

def remove_cart(request,product_id): #function will receive product_id in which - button is clicked
    cart=Cart.objects.get(cart_id=__get_id(request)) #accessing the cart first based on session_id
    product = get_object_or_404(Product,id=product_id) # access the product: to access the same product/cart_item of the cart
    cart_item=CartItem.objects.get(cart=cart,product=product) #accessing the cart_item/product of the cart
    if cart_item.quantity > 1:
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request,product_id):
    cart=Cart.objects.get(cart_id=__get_id(request))
    product=Product.objects.get(id=product_id)
    cart_item=CartItem.objects.get(product=product,cart=cart)
    cart_item.delete()
    return redirect('cart')

def cart(request,total=0,quantity=0,cart_items=None):
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