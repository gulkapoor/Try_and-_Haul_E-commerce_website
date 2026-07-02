from django.db import models
from django.db.models import Max, UniqueConstraint
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
import uuid

# User Model
class User(AbstractUser):
    # While creating account
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'phone']

    def __str__(self):
        return self.email 


# Brand Model
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to="images/", null=True, blank=True)
    IsFeatured = models.BooleanField(default=False)
    email = models.EmailField(unique=True, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Category Model (Men, Women, Unisex)
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Product Model (Tshirt, Shirt, Trouser)
class ProductType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Color Model
class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hexCode = models.CharField(max_length=7, help_text="Hex code for color")

    def __str__(self):
        return self.name

# Size Model
class Size(models.Model):
    size_label = models.CharField(max_length=10, unique=True)  # e.g., S, M, L, XL

    def __str__(self):
        return self.size_label

# Size Guide Model (Different for each Brand)
class SizeGuide(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="size_guides")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="size_guides") # male, female
    ProductType = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name="size_guides")  # Trouser, Trouser
    
    size_label = models.CharField(max_length=10)  # Example: S, M, L, XL
    Chest = models.CharField(max_length=10, blank=True, null=True)
    FrontLength = models.CharField(max_length=10, blank=True, null=True)
    Accross_Shoulders = models.CharField(max_length=10, blank=True, null=True)
    Sleeve_length = models.CharField(max_length=10, blank=True, null=True)  
    Waist = models.CharField(max_length=10, blank=True, null=True)  
    Inseam_Length = models.CharField(max_length=10, blank=True, null=True)  
    Hip = models.CharField(max_length=10, blank=True, null=True)  
    

    class Meta:
        unique_together = ('brand', 'category', 'size_label')  # Ensures unique size per brand-category

    def __str__(self):
        return f"{self.brand.name} - {self.category.name} ({self.size_label})"
    

# Listing Model (Main Product Listing)
class Listing(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    productType = models.ForeignKey(ProductType, on_delete=models.CASCADE, blank=True, null=True)
    uniqueLabel = models.PositiveIntegerField(blank=True, null=True)
    colors = models.ManyToManyField(Color)
    sizes = models.ManyToManyField(Size)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discountedPrice = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    productDetails = models.TextField(blank=True, null=True)
    deliveryTime = models.CharField(max_length=255, default="5-7 days")
    createdAt = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    returnEligible = models.BooleanField(default=False)
    exchangeEligible = models.BooleanField(default=False)

    bestSelling = models.BooleanField(default=False)
    newArrival = models.BooleanField(default=False)
    limitedTime = models.BooleanField(default=False)
    specialOffer = models.BooleanField(default=False)
    

    class Meta:
        constraints = [
            UniqueConstraint(fields=['productType', 'uniqueLabel'], name='unique_product_label')
        ]

    def save(self, *args, **kwargs):
        # Assign uniqueLabel if not already set
        if not self.uniqueLabel and self.productType:
            last_label = Listing.objects.filter(productType=self.productType).aggregate(Max('uniqueLabel'))['uniqueLabel__max']
            self.uniqueLabel = 1 if last_label is None else last_label + 1
        
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


        super().save(*args, **kwargs)


    def final_price(self):
        return self.discountedPrice if self.discountedPrice else self.price

    def __str__(self):
        return f"{self.brand} - {self.name}"
    
class Stock(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="stock")
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)  # Track stock for each size

    class Meta:
        unique_together = ('listing', 'size')  # Ensure each listing-size pair is unique

    def __str__(self):
        return f"{self.listing.name} - {self.size.size_label}: {self.quantity} left"


# Image Model (To Store Multiple Images)
class Image(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="images/")

    def __str__(self):
        return f"Image for {self.listing.name}"

class Wishlist(models.Model):
    wishlistUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlistUser")
    wishlistItem = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="wishlistedItem")

    def __str__(self):
        return f"{self.wishlistItem.name} wishlisted by {self.wishlistUser.username}"

class Cart(models.Model):
    cartUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cartUser")
    cartItem = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="cartItem")
    cartSize = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="size")
    cartQuantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.cartItem.name} size {self.cartSize} in cart of {self.cartUser.username} "
    
class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addressUser")
    fullName = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    pincode = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user} : {self.fullName} "
    
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    percentage = models.IntegerField()
    minCartValue = models.IntegerField()
    maxDiscount = models.IntegerField()
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.code
    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, null=True, blank=True) # Razorpay order ID
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    address = models.ForeignKey(UserAddress, on_delete=models.SET_NULL, null=True)
    items = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, null=True, blank=True) # Razorpay payment ID
    signature = models.CharField(max_length=256, null=True, blank=True) # Razorpay signature
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    payment_status = models.CharField(max_length=20, default='PENDING') # e.g., PENDING, SUCCESS, FAILED
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.payment_status}"