from django.contrib import admin
from .models import UserProfile, Brand, Category, Product
# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name','user','role')
    list_filter = ('role',)
    search_fields = ('name', 'user__username','role')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('brand_name','owner','description')
    list_filter = ('owner__role',)
    search_fields = ('brand_name', 'owner__name')
    
    def save_model(self,request, obj, form, change):
        # Ensure clean() is called so non-sellers can't be owners
        obj.full_clean()# manually validate with your clean() logic
        super().save_model(request, obj, form, change)
  

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)
    search_fields = ('category_name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'brand', 'owner', 'category', 'status', 'quantity')
    list_filter = ('status', 'category', 'brand')
    search_fields = ('product_name', 'sku', 'brand__brand_name')
    exclude = ('owner',)

    def save_model(self,request, obj, form, change):
        if not change or not obj.owner_id:
            try:
                obj.owner = UserProfile.objects.get(user = request.user)
            except Exception as e:
                raise Exception("You must have a valid UserProfile to create or update a product.")
        obj.full_clean()
        super().save_model(request, obj, form, change)