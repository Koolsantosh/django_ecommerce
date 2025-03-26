from django.shortcuts import render,get_object_or_404,HttpResponse
from .models import Product
from category.models import Category
from carts.models import Cart,CartItem
from carts.views import __get_id
from django.core.paginator import Paginator
from django.db.models import Q

# Create your views here.

def store(request,category_slug=None):
    
    categories=None
    products = None

    category_list =Category.objects.all()

    if category_slug !=None:
        categories=get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=categories,is_available=True)

        paginator = Paginator(products,3)
        page = request.GET.get('page')
        paged_products =paginator.get_page(page)

        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')

        paginator = Paginator(products,3)
        page = request.GET.get('page')
        paged_products =paginator.get_page(page)

        product_count=products.count()
    
    context={
        'products':paged_products,
        'product_count':product_count,
        'category_list':category_list,
    }
    
    return render(request,'store/store.html',context)

def product_detail(request,category_slug,product_slug):
    try:
        single_product=Product.objects.get(category__slug=category_slug, slug=product_slug) # category is field of Category Model __ is use to access it linked Model i.e Product: field is slug

        in_cart = CartItem.objects.filter(cart__cart_id=__get_id(request),product=single_product).exists() # accessing parent field using foreign key filed
        # return HttpResponse(in_cart)
        # exit()
    except Exception as e:
        raise e
    
    context={
        'single_product':single_product,
        'in_cart':in_cart,
    }
    return render(request,'store/product_detail.html',context)

def search(request):
    products=[]
    product_count=0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            # products=Product.objects.order_by('-created_date').filter(description__icontains=keyword) # _icontains will check if text exist in the description
            products=Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count=products.count()
    context ={
        'products':products,
        'product_count':product_count,
    }
    return render(request,'store/store.html',context)