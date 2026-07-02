from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import uuid, json, traceback, os, hmac, hashlib, base64
from django.core.mail import send_mail
from django.template.loader import render_to_string
import razorpay
from decimal import Decimal
import string, random








from .models import Listing, Category, ProductType, Listing, Brand, User, Cart, Wishlist, Size, Stock, UserAddress, Coupon, SizeGuide, Order, Image, Payment, Color


# Create your views here.
def index(request):
    return render(request, "index.html")

def login_view(request):
    if request.user.is_authenticated:
        return reverse("index")
    
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")

def signup_view(request):
    if request.user.is_authenticated:
        return reverse("index")
    
    if request.method == "POST":
        firstName_ = request.POST["firstName"]
        lastName_ = request.POST["lastName"]
        email_ = request.POST["email"]
        phone_ = request.POST["phone"]
        

        # Ensure password matches confirmation
        password_ = request.POST["password"]
        confirmation_ = request.POST["confirmation"]
        if password_ != confirmation_:
            return render(request, "signup.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username=email_,
                firstName=firstName_,
                lastName=lastName_, 
                email=email_, 
                phone=phone_,
                password=password_)
            user.save()
        except IntegrityError:
            return render(request, "signup.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "signup.html")

@login_required
def logout_view(request):
    try:
        logout(request)
        return HttpResponseRedirect(reverse("index"))
    except:
        return HttpResponseRedirect(reverse("index"))


@login_required(login_url="/login")
def orders(request):
    userOrders = Order.objects.filter(user=request.user).order_by('-created_at')

    enriched_orders = []
    for order in userOrders:
        enriched_items = []
        for item in order.items or []:
            try:
                listing = Listing.objects.get(id=item['cartItem_id'])
                size = Size.objects.get(id=item['cartSize_id'])
                image_obj = listing.images.first()

                enriched_items.append({
                    "productName": listing.name,
                    "size": size.size_label,
                    "quantity": item['cartQuantity'],
                    "image": image_obj.image.url if image_obj else None
                })
            except Exception as e:
                print(f"Error enriching item: {e}")
                continue

        try:
            payment_status = order.payment.payment_status
        except Payment.DoesNotExist:
            payment_status = "PENDING"

        enriched_orders.append({
            "order_id": order.order_id,
            "created_at": order.created_at,
            "status": payment_status,
            "amount": order.total_amount,
            "discount": order.discount,
            "orderAddress": order.address,
            "items": enriched_items,
        })

    return render(request, "orders.html", {
        "orders": enriched_orders,
    })



@login_required(login_url="/login")
def wishlist(request):
    user = request.user
    listings = Wishlist.objects.filter(wishlistUser=user)
    
    return render(request,"wishlist.html", {
        "listings": listings,
    })


@login_required(login_url="/login")
def cart(request):
    listings = Cart.objects.filter(cartUser=request.user)
    stock_issues = {}  # Dictionary to store items with stock issues

    for item in listings:
        try:
            stock = Stock.objects.get(listing=item.cartItem, size=item.cartSize)
            if stock.quantity < item.cartQuantity:
                stock_issues[item.id] = {
                    'item_name': item.cartItem.name,
                    'size': item.cartSize.size_label,
                    'available': stock.quantity,
                    'requested': item.cartQuantity
                }
        except Stock.DoesNotExist:
            stock_issues[item.id] = {
                'item_name': item.cartItem.name,
                'size': item.cartSize.size_label,
                'available': 0,
                'requested': item.cartQuantity
            }

    return render(request, "cart.html", {
        "listings": listings,
        "stock_issues": stock_issues,
    })

def apply_coupon(request):
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        total_amount = float(request.POST.get("total_amount", 0))

        try:
            coupon = Coupon.objects.get(code=coupon_code, isActive=True)
            if total_amount >= coupon.minCartValue:
                discount_amount = (total_amount * coupon.percentage) / 100
                discount_amount = min(discount_amount, coupon.maxDiscount)

                return JsonResponse({
                    "success": True,
                    "discount": discount_amount,
                    "message": f"Coupon {coupon.code} applied successfully!",
                })
            else:
                return JsonResponse({
                    "success": False,
                    "message": f"Minimum order value must be ₹{coupon.minCartValue} to use this coupon."
                })
        except Coupon.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invalid or expired coupon code."})
    
    return JsonResponse({"success": False, "message": "Invalid request."})


def storeOrderDetails(request, totalAmount, totalMRP, discount, couponDiscount):
    if request.method == "POST":
        if "saveAddressBtn" in request.POST:
            fullName = request.POST.get("full-name")
            phone = request.POST.get("phone")
            address = request.POST.get("address")
            city = request.POST.get("city")
            state = request.POST.get("state")
            pincode = request.POST.get("pincode")

            address = UserAddress(
                user=request.user,
                fullName=fullName,
                phone=phone,
                address=address,
                city=city,
                state=state,
                pincode=pincode
            )
            address.save()
        
        if "addAddressBtn" in request.POST:
            fullName = request.POST.get("full-name")
            phone = request.POST.get("phone")
            address = request.POST.get("address")
            city = request.POST.get("city")
            state = request.POST.get("state")
            pincode = request.POST.get("pincode")

            address = UserAddress(
                user=request.user,
                fullName=fullName,
                phone=phone,
                address=address,
                city=city,
                state=state,
                pincode=pincode
            )
            address.save()


        if "removeAddress" in request.POST:
            addressID = request.POST.get("addressID")
            
            address = get_object_or_404(UserAddress, id=addressID)
            address.delete()


        # Takes to payment page
        if "continueToPaymentBtn" in request.POST: 
            orderAddress = request.POST.get("selectedAddress")
            orderAddressObj = get_object_or_404(UserAddress, id=orderAddress)

            # Convert the object into a dictionary (store only essential fields)
            orderAddressData = {
                "fullName": orderAddressObj.fullName,
                "phone": orderAddressObj.phone,
                "address": orderAddressObj.address,
                "city": orderAddressObj.city,
                "state": orderAddressObj.state,
                "pincode": orderAddressObj.pincode,
            }

            request.session["payment_details"] = {
                "paymentAddress": orderAddressData,
                "paymentAmount": totalAmount
            }
            return redirect(reverse('payment'))


        # Redirect back to address page
        request.session['order_details'] = {
        'totalAmount': totalAmount,
        'totalMRP': totalMRP,
        'discount': discount,
        'couponDiscount': couponDiscount,
        }
        return redirect(reverse('address'))


    request.session['order_details'] = {
        'totalAmount': totalAmount,
        'totalMRP': totalMRP,
        'discount': discount,
        'couponDiscount': couponDiscount,
    }
    return redirect(reverse('address'))




def address(request):
    if 'order_details' not in request.session:
        return HttpResponseForbidden("Access Denied. Please proceed through the checkout.")

    cartItems = Cart.objects.filter(cartUser=request.user)
    # Convert queryset to a list of dictionaries
    cart_items_data = list(cartItems.values())  
    cart_items_json = json.dumps(cart_items_data)


    order_details = request.session.get('order_details')  # Remove after use
    addresses = UserAddress.objects.filter(user=request.user)
    return render(request, 'userAddress.html', {
        "order_details":order_details,
        "addresses": addresses,
        "cart_items_data": cart_items_data,
        "cartItems": cart_items_json
    })


def category(request, category_slug):

    category_aliases = {
        "male": "men",
        "female": "women",
    }

    normalized_category = category_aliases.get(category_slug, category_slug)

    category = get_object_or_404(Category, slug=normalized_category)
    listings = Listing.objects.filter(category=category)

    return render(request, "category.html", {
        "category": category,
        "listings": listings,
    })

def productType(request, category_slug, productType_slug):

    # CATEGORY NORMALIZATION
    category_aliases = {
        "male": "men",
        "female": "women",
    }

    # PRODUCT NORMALIZATION
    product_aliases = {
        "top": "tops",
        "tops": "tops",

        "tshirt": "t-shirt",
        "tee": "t-shirt",
        "t-shirt": "t-shirt",

        "pant": "pants",
        "pants": "pants",

        "trouser": "trousers",
        "trousers": "trousers",

        "short": "shorts",
        "shorts": "shorts",

        "bag": "bags",
        "bags": "bags",

        "cap": "cap",
        "caps": "cap",

        "watch": "watch",
        "watches": "watch",

        "belt": "belt",
        "belts": "belt",
    }

    normalized_category = category_aliases.get(category_slug, category_slug)
    normalized_product = product_aliases.get(productType_slug, productType_slug)

    category = get_object_or_404(Category, slug=normalized_category)
    product_type = get_object_or_404(ProductType, slug=normalized_product)

    if normalized_category in ["men", "women"]:
        listings = Listing.objects.filter(
            category__slug__in=[normalized_category, "unisex"],
            productType=product_type
        )
    else:
        listings = Listing.objects.filter(
            category=category,
            productType=product_type
        )

    return render(request, "listing.html", {
        "listings": listings,
        "category": category.name,
        "productType": product_type.name
    })

def item(request, category_slug, productType_slug, listing_slug):
    category = get_object_or_404(Category, slug=category_slug)
    productType = get_object_or_404(ProductType, slug=productType_slug)
    listing = get_object_or_404(Listing, category=category, productType=productType, slug=listing_slug)

    size_guide = SizeGuide.objects.filter(brand=listing.brand, category=listing.category, ProductType=listing.productType)

    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(wishlistUser=request.user, wishlistItem=listing).exists()
    else:
        is_in_wishlist = False

    if request.method == "POST":
        
        # Add Item or increase quanity of cart from listing page
        if "addCart" in request.POST:   
            selectedSize = request.POST.get("size")
            
            if not selectedSize:
                messages.error(request, "Please select a size before adding to the cart.")
                return redirect(request.META.get("HTTP_REFERER", "index"))

            sizeInstance = get_object_or_404(Size, size_label=selectedSize)

            # Get stock for the selected size
            stock_item = Stock.objects.filter(listing=listing, size=sizeInstance).first()

            if not stock_item or stock_item.quantity <= 0:
                messages.error(request, "This size is out of stock!")
                return redirect(request.META.get("HTTP_REFERER", "index"))

            # Check if the item with the same size already exists in the cart
            cart_item, created = Cart.objects.get_or_create(
                cartUser=request.user, 
                cartItem=listing, 
                cartSize=sizeInstance,
            )

            if not created:  # If the item already exists, increase quantity
                if cart_item.cartQuantity + 1 > stock_item.quantity:
                    messages.error(request, "Not enough stock available!")
                else:
                    cart_item.cartQuantity += 1
                    cart_item.save()
                    messages.info(request, "Increased quantity in cart.")
            else:
                messages.success(request, "Item added to cart!")

        # Add to wishlist through item page
        if "addWishlist" in request.POST:
            wishlist_item = Wishlist.objects.filter(wishlistUser=request.user, wishlistItem=listing)
            if wishlist_item.exists():
                wishlist_item.delete()  # Remove from wishlist
                is_in_wishlist = False
                messages.success(request, "Item removed from wishlist.")  
            else:
                Wishlist.objects.create(wishlistUser=request.user, wishlistItem=listing) # Add to the Wishlist
                messages.success(request, "Item added to wishlist!")  
                is_in_wishlist = True

            return redirect(reverse("item", args=[category_slug, productType_slug, listing_slug]))       
        
        # Remove from Wishlist from wishlist page
        if "removeWishlistThroughWishlist" in request.POST:
            wishlist_item = Wishlist.objects.filter(wishlistUser=request.user, wishlistItem=listing)
            if wishlist_item.exists():
                wishlist_item.delete()  # Remove from wishlist
                is_in_wishlist = False
                messages.success(request, "Item removed from wishlist.")  
            else:
                Wishlist.objects.create(wishlistUser=request.user, wishlistItem=listing) # Add to the Wishlist
                messages.success(request, "Item added to wishlist!")  
                is_in_wishlist = True

            return redirect(reverse("wishlist"))
        
        if "removeCartItemFromCart" in request.POST:
            selectedSize = request.POST.get("size")
            sizeInstance = get_object_or_404(Size, size_label=selectedSize)
            
            item = Cart.objects.filter(cartUser=request.user, cartItem=listing, cartSize=sizeInstance)
            item.delete()
            return redirect(reverse("cart"))
        
        # Decrease the quantity of an item in cart
        if "decreaseQuantity" in request.POST:
            selectedSize = request.POST.get("size")
            sizeInstance = get_object_or_404(Size, size_label=selectedSize)

            # Get the object
            cart_item = get_object_or_404(
                Cart,
                cartUser=request.user, 
                cartSize=sizeInstance,
            )

            if cart_item.cartQuantity == 1:
                cart_item.delete()
                request.session["cart_message"] = {
                    "message": f"Removed {cart_item.cartItem.name} from cart.",
                    "cart_item_id": cart_item.id
                }
            else:
                cart_item.cartQuantity -= 1  # Decrease Quantity
                cart_item.save()
                request.session["cart_message"] = {
                    "message": f"Decreased quantity for {cart_item.cartItem.name}.",
                    "cart_item_id": cart_item.id
                }

            return redirect(reverse("cart"))

        # Increase the quantity of an item in the cart
        if "increaseQuantity" in request.POST:
            selectedSize = request.POST.get("size")
            sizeInstance = get_object_or_404(Size, size_label=selectedSize)

            # Get the object
            cart_item = get_object_or_404(
                Cart,
                cartUser=request.user, 
                cartSize=sizeInstance,
            )

            stock_item = Stock.objects.filter(listing=cart_item.cartItem, size=sizeInstance).first()

            if not stock_item or stock_item.quantity <= 0:
                request.session["cart_message"] = {
                    "message": "This size is out of stock!",
                    "cart_item_id": cart_item.id
                }
                return redirect(request.META.get("HTTP_REFERER", "index"))

            if cart_item.cartQuantity + 1 > stock_item.quantity:
                request.session["cart_message"] = {
                    "message": "Not enough stock available!",
                    "cart_item_id": cart_item.id
                }
            else:
                cart_item.cartQuantity += 1
                cart_item.save()
                request.session["cart_message"] = {
                    "message": f"Increased quantity for {cart_item.cartItem.name}.",
                    "cart_item_id": cart_item.id
                }

            return redirect(reverse("cart"))


    return render(request, "item.html", {
        "listing": listing,
        "is_in_wishlist": is_in_wishlist,
        "size_guide": size_guide
    })

# Clears the session message after displaying it
def clear_cart_message(request):
    request.session.pop("cart_message", None)
    return JsonResponse({"success": True})

def search_results(request):
    if request.method == "POST":
        query = request.POST.get("q")
        results = []

        if query:
            results = Listing.objects.filter(
            Q(name__icontains=query) |  # Search in listing names
            Q(brand__name__icontains=query)  # Search in brand names
        ).distinct()

        return render(request, "listing.html", {"query": query, "listings": results})


def allProducts(request):
    listings = Listing.objects.all().order_by("-createdAt")
    return render(request, "listing.html", {
        'listings': listings,
        "category": "All Products"
    })


def brand(request, brand_slug):
    brand = get_object_or_404(Brand, slug=brand_slug)
    listings = Listing.objects.filter(brand=brand)

    return render(request, "listing.html", {
        "listings": listings,  
    })


def brandlist(request):
    brands = Brand.objects.all()
    return render(request, "brandlist.html", {
        "brands": brands
    })


def bestSellers(request):
    listings = Listing.objects.filter(bestSelling=True)
    return render(request, "listing.html", {
        "listings": listings
    })


def newArrivals(request):
    listings = Listing.objects.filter(newArrival=True)
    return render(request, "listing.html", {
        "listings": listings
    })

def limitedDrops(request):
    listings = Listing.objects.filter(limitedTime=True)
    return render(request, "listing.html", {
        "listings": listings
    })


def specialOffers(request):
    listings = Listing.objects.filter(specialOffer=True)
    return render(request, "listing.html", {
        "listings": listings
    })



def terms(request):
    return render(request, "terms.html")


def faq(request):
    return render(request, "FAQ.html")


def returnExchange(request):
    return render(request, "returnExchange.html")


def aboutUs(request):
    return render(request, "aboutUs.html")

@login_required
def process_order(request):
    if request.method == "POST":
        user = request.user
        amount = request.POST.get("amount")
        discount = request.POST.get("discount")
        coupon_discount = request.POST.get("couponDiscount")
        address_id  = request.POST.get("selectedAddress")

        address = get_object_or_404(UserAddress, id=address_id, user=user)
        total_discount = float(discount or 0) + float(coupon_discount or 0)
        cart_items_raw = request.POST.get("cartItems")
        cart_items_data = json.loads(cart_items_raw) if cart_items_raw else []

        # Create Order
        order = Order.objects.create(
            user=user,
            total_amount=amount,
            discount=total_discount,
            address=address,
            items=cart_items_data,
        )
        order.save()

        # Save order ID in session if needed, or redirect directly to payment
        return redirect('initiate_payment', order_id=order.id)

@login_required
def initiate_payment(request, order_id):
    

    order = get_object_or_404(Order, id=order_id)
    amount = order.total_amount # Amount in paise

    # Save cart items to order if not already saved
    if not order.items:
        user_cart_items = Cart.objects.filter(cartUser=request.user)
        cart_data = list(user_cart_items.values())
        order.items = cart_data
        order.save()


    # Initialize Razorpay client based on the environment
    if settings.DEBUG:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID_TEST, settings.RAZORPAY_KEY_SECRET_TEST))
    else:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID_LIVE, settings.RAZORPAY_KEY_SECRET_LIVE))

    # Create a Razorpay order
    razorpay_order = client.order.create(dict(amount=int(order.total_amount * 100), currency='INR', receipt=f'order_{order.id}'))
    order.order_id = razorpay_order['id']
    order.save()

    context = {
        'order': order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID_TEST if settings.DEBUG else settings.RAZORPAY_KEY_ID_LIVE,
    }
    return render(request, 'payment.html', context)

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        order = Order.objects.get(order_id=order_id)

        if Payment.objects.filter(order=order).exists():
            return render(request, 'paymentSuccess.html', {'payment': Payment.objects.get(order=order)})

        # Initialize Razorpay client
        if settings.DEBUG:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID_TEST, settings.RAZORPAY_KEY_SECRET_TEST))
        else:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID_LIVE, settings.RAZORPAY_KEY_SECRET_LIVE))

        if Payment.objects.filter(order=order).exists():
            return JsonResponse({'status': 'already_exists'})

        try:
            # Verify payment signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })


            # Payment Success Mail
            enriched_items = []
            for item in order.items:
                try:
                    listing = Listing.objects.get(id=item["cartItem_id"])
                    size = Size.objects.get(id=item["cartSize_id"])
                    quantity = item["cartQuantity"]

                    enriched_items.append({
                        'listing': listing,
                        "brand": listing.brand.name,
                        "name": listing.name,
                        "color": listing.colors.first().name,
                        "size": size.size_label,
                        "quantity": quantity
                    })
                except Exception as e:
                    print("Error enriching item for email:", e)
                    continue

            admin_email = settings.DEFAULT_FROM_EMAIL
            subject = f"New Order Placed - Order #{order.order_id}"
            context = {
                'order': order,
                'user': request.user,
                'payment': {
                    'id': payment_id,
                    'amount': order.total_amount,
                    'date': order.created_at,
                },
                'items': enriched_items,
                'order_address': order.address
            }
            print("🥰enriched_items", enriched_items)
            message = render_to_string('emails/admin_order_details.html', context)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin_email], html_message=message)
            print(f"Admin notification email sent for Order #{order.order_id}")

            payment = Payment.objects.create(
                order=order,
                payment_id=payment_id,
                signature=signature,
                amount=order.total_amount,
                payment_status='SUCCESS'
            )
            print("Order Items:", order.items)

            # Reduce stock
            for cart_item in order.items:
                print("Cart item:", cart_item)
                listing_id = cart_item.get("cartItem_id")
                size_id = cart_item.get("cartSize_id")
                quantity = cart_item.get("cartQuantity", 1)

                try:
                    print("Trying to fetch stock for listing ID:", listing_id, "and size ID:", size_id)
                    stock_obj = Stock.objects.get(listing_id=listing_id, size_id=size_id)
                    if stock_obj.quantity >= quantity:
                        stock_obj.quantity -= quantity
                    else:
                        stock_obj.quantity = 0
                    stock_obj.save()
                except Stock.DoesNotExist:
                    # Optional: Log this or handle it more gracefully
                    continue

            enriched_items = []
            # getting the items details to pass into success page
            for item in order.items:
                try:
                    size = Size.objects.get(id=item['cartSize_id'])
                    listing = Listing.objects.get(id=item['cartItem_id'])
                    image = listing.images.first()
                    enriched_items.append({
                        'listing': listing,
                        'size': size,
                        'quantity': item['cartQuantity'],
                        'image': image.image.url if image else None
                    })
                except Exception as e:
                    print("Error enriching item:", e)
                    continue

            # Clear cart
            Cart.objects.filter(cartUser=request.user).delete()

            return render(request, 'paymentSuccess.html', {
                'payment': payment,
                'items': enriched_items
                })

        except Exception as e:
            # Prevent duplicate failed payments
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'payment_id': payment_id,
                    'signature': signature,
                    'amount': order.total_amount,
                    'payment_status': 'FAILED'
                }
            )
            return render(request, 'paymentFailed.html', {'error': str(e), 'payment': payment})

    return redirect('payment_failed')

@login_required
def payment_failed(request):
    return render(request, 'paymentFailed.html')

