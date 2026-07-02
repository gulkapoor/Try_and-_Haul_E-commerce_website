from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('initiate/<int:order_id>/', views.initiate_payment, name='initiate_payment'),

    # Listings
    path('all-products', views.allProducts, name="allProducts"),    
    path('best-sellers', views.bestSellers, name="bestSellers"),
    path('new-arrivals', views.newArrivals, name="newArrivals"),
    path('special-offers', views.specialOffers, name="specialOffers"),
    path('limited-drops', views.limitedDrops, name="limitedDrops"),
    

    # Login     
    path("login", views.login_view, name="login"),
    path('signup', views.signup_view, name="signup"),
    path('logout', views.logout_view, name="logout"),

    path("search/", views.search_results, name="search_results"),
    
    # After Login
    path('wishlist', views.wishlist, name="wishlist"),
    path('cart', views.cart, name="cart"),
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path("store-order/<str:totalAmount>/<str:totalMRP>/<str:discount>/<str:couponDiscount>/", views.storeOrderDetails, name="storeOrderDetails"),
    path("address/", views.address, name="address"),
    path("orders", views.orders, name="orders"),
    


    path('process-order/', views.process_order, name='process_order'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),




    # Help
    path('terms-conditions', views.terms, name="termsAndConditions"),
    path('FAQ', views.faq, name="FAQ"),
    path('return-exchange-policy', views.returnExchange, name="returnExchangePolicy"),
    path('about-us', views.aboutUs, name="aboutUs"),
    
    # Brandlist
    path('brandlist/', views.brandlist, name='brandlist'),
    
    # Categorise Brands 
    path('brandlist/<slug:brand_slug>/', views.brand, name="brand"),

    # Categorise gender, type and product
    path('<slug:category_slug>/', views.category, name="category"),
    path('<slug:category_slug>/<slug:productType_slug>/', views.productType, name="productType"),
    path('<slug:category_slug>/<slug:productType_slug>/<slug:listing_slug>/', views.item, name='item'),
]
