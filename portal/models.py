from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
# Create your models here.

PRODUCT_IMAGE_PATH = 'PRODUCT_IMAGES/'

class UserProfile(models.Model):
    userRole = (
        ('buyer', 'Buyer'),
        ('seller', "Seller")
    )
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10,choices=userRole)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name.upper()} - {self.role.upper()}"
    
class Brand(models.Model):
    brand_name = models.CharField(max_length=50)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role':'seller'})
    description = models.TextField()

    def clean(self):
        if hasattr(self, 'owner') and self.owner:
            if self.owner.role != 'seller':
                raise ValidationError("Only sellers can own brands.")
    class Meta:
        unique_together = ('brand_name', 'owner')

    def __str__(self):
        return self.brand_name.upper()

class Category(models.Model):
    category_name = models.CharField(max_length=50)
    category_description = models.TextField()
    def __str__(self):
        return self.category_name.upper() 
    
class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=50)
    desc = models.TextField()
    status = models.BooleanField(default=True) #Product.objects.filter(status=True)  # Only active products
    image = models.ImageField(upload_to=PRODUCT_IMAGE_PATH)
    quantity = models.IntegerField()
    sku = models.CharField(max_length=12)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'seller'})

    height_cm = models.DecimalField(max_digits=6, decimal_places=2, help_text="Height in centimeters")
    width_cm = models.DecimalField(max_digits=6, decimal_places=2, help_text="Width in centimeters")

    def __str__(self):
        return self.product_name.upper()

    # Shell : Product.objects.filter(status__isnull=True).update(status=True)
    # Shell : Product.objects.all().update(status=True)
