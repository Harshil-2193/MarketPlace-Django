from django.test import TestCase
# import pytest
from django.urls import reverse
from django.core.paginator import PageNotAnInteger,EmptyPage
from django.contrib.messages import get_messages
from .models import Brand, Product,User,UserProfile,Category
from .views import portal
# Create your tests here.

class PortalViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        # Create test user
        cls.user_seller = User.objects.create(username="seller1",password="test123")
        cls.user_buyer = User.objects.create(username="buyer1",password="test123")
        
        # Create test user_profiles
        cls.seller_profile = UserProfile.objects.create(
            user=cls.user_seller,
            role='seller',
            name = 'Test Seller'
        )
        cls.buyer_profile = UserProfile.objects.create(
            user=cls.user_seller,
            role='buyer',
            name = 'Test buyer'
        )

        # Create test Brand
        cls.brand = Brand.objects.create(
            brand_name='TestBrand',
            owner=cls.seller_profile,
            description='Test description'
        )

        #Create test Category
        cls.category = Category.objects.create(
            category_name='Electronics',
            category_description='Electronic items'
        )

        # Active Products
        for i in range(1, 15):
            Product.objects.create(
                product_name=f'Product {i}',
                desc=f'Description {i}',
                status=True,
                image='products/test.jpg',
                quantity=10,
                sku=f'SKU{i:03d}',
                category=cls.category,
                brand=cls.brand,
                owner=cls.seller_profile,
                height_cm=10.0,
                width_cm=5.0
            )
        
        # Inactive Products
        Product.objects.create(
            product_name='Inactive Product',
            desc='Inactive item',
            status=False,
            image='products/inactive.jpg',
            quantity=0,
            sku='INACT001',
            category=cls.category,
            brand=cls.brand,
            owner=cls.seller_profile,
            height_cm=5.0,
            width_cm=5.0
        )
    
    def test_portal_view_returns_200(self):
        response = self.client.get(reverse('portal'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portal/dashboard.html')

    def test_portal_view_shows_active_products_only(self):
        response = self.client.get(reverse('portal'))
        products = response.context['products']
        self.assertEqual(products.paginator.count,14) #For Active Products only 
        self.assertNotIn('Inactive Product', [p.product_name for p in products])
    
    # Brand Filtering
    def test_brand_filter_works(self):
        # Create Second Brand
        brand2 = Brand.objects.create(
            brand_name='Brand 2',
            owner = self.seller_profile,
            description = "other Brand"
        )

        # Add product to second brand
        Product.objects.create(
            product_name='Brand 2 Product',
            desc='Test',
            status=True,
            image='products/other.jpg',
            quantity=5,
            sku='OTHER001',
            category=self.category,
            brand=brand2,
            owner=self.seller_profile,
            height_cm=8.0,
            width_cm=8.0
        )

        response = self.client.get(reverse('portal'), {'brand':"TestBrand"})
        products = response.context['products']
        self.assertEqual(products.paginator.count, 14)
        self.assertNotIn('Other Brand Product', [p.product_name for p in products])






