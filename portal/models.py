from django.db import models
from django.contrib.auth.models import User
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

class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=50)
    desc = models.TextField()
    status = models.BooleanField(default=True)
    image = models.ImageField(upload_to=PRODUCT_IMAGE_PATH)
    quantity = models.IntegerField()
    sku = models.CharField(max_length=12)

    def __str__(self):
        return self.product_name.upper()
