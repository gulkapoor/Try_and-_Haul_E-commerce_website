from django.contrib import admin
from .models import Brand, Category, Color, Size, SizeGuide, Listing, Image, ProductType, User, Wishlist, Cart, Stock, UserAddress, Coupon, Order, Payment

admin.site.register(User)

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'discountedPrice')
    list_filter = ('brand', 'category')
    search_fields = ('name', 'brand__name')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('listing', 'image')
    list_filter = ('listing__name',)
    search_fields = ('listing__name',)

admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(SizeGuide)
admin.site.register(ProductType)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(Stock)
admin.site.register(UserAddress)
admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(Payment)
