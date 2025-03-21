from django.db import models
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=50,unique=True)
    slug = models.SlugField(max_length=100,unique=True)
    description = models.TextField(max_length=255,blank=True)
    cat_image = models.ImageField(upload_to='photos/categories',blank=True)

    class Meta:
        verbose_name='category'
        verbose_name_plural='Categories'

    def get_url(self):
        return reverse('products_by_category',args=[self.slug]) #here product_by_category is name of urls in store:urls.py file and self.slug represent slug of calling object of Category
    
    def __str__(self):
        return self.category_name