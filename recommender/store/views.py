from venv import logger
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from sympy import Min
from .models import Product, Purchase, Feedback, Category
from .forms import UserFeedbackForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth import logout

# Signup View
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful signup
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


# Product List
@login_required
def product_list(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    page_number = request.GET.get('page', 1)

    if category_id:
        products = Product.objects.filter(category_id=category_id).order_by('id')
    else:
        products = Product.objects.all().order_by('id')

    paginator = Paginator(products, 10)
    page_obj = paginator.get_page(page_number)

    # Get purchased products (for "Already Purchased" label)
    purchased_products = Purchase.objects.filter(user=request.user).values_list('product_id', flat=True)
    
    # Get cart items (for cart count)
    cart = request.session.get('cart', {})
    cart_item_count = sum(cart.values())

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'purchased_products': purchased_products,
        'cart_item_count': cart_item_count,
    })

@login_required
def view_cart(request):
    """Show items in cart (not yet purchased)."""
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': item_total,
        })
        total_price += item_total

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if already purchased
    if Purchase.objects.filter(user=request.user, product=product).exists():
        messages.info(request, f"You already own {product.name}")
        return redirect_with_filters(request, 'product_list')
    
    # Add to cart
    cart = request.session.get('cart', {})
    cart[str(product.id)] = cart.get(str(product.id), 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    
    messages.success(request, f"{product.name} added to cart!")
    return redirect_with_filters(request, 'product_list')

# Add this helper function to your views.py
def redirect_with_filters(request, view_name):
    """Redirect while preserving all GET parameters"""
    url = reverse(view_name)
    params = request.GET.urlencode()
    if params:
        url = f"{url}?{params}"
    return redirect(url)

@login_required
def purchase_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    # Get quantity from cart or default to 1
    quantity = cart.get(str(product.id), 1)
    
    # Check if already purchased
    purchase, created = Purchase.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        # If already purchased, increase quantity
        purchase.quantity += quantity
        purchase.save()
    
    # Remove from cart
    if str(product.id) in cart:
        del cart[str(product.id)]
        request.session['cart'] = cart
        request.session.modified = True
    
    messages.success(request, f"Purchased {product.name} (x{quantity})")
    return redirect('view_cart')

@login_required
def purchase_all(request):
    cart = request.session.get('cart', {})
    purchased_items = 0
    
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        
        purchase, created = Purchase.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            purchase.quantity += quantity
            purchase.save()
        
        purchased_items += quantity
    
    # Clear cart
    request.session['cart'] = {}
    request.session.modified = True
    
    messages.success(request, f"Purchased {purchased_items} items!")
    return redirect('view_cart')


@login_required
def remove_from_cart(request, product_id):
    """Remove an item from cart (without purchasing)."""
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Item removed from cart.")

    return redirect('view_cart')

@login_required
def purchase_history(request):
    purchases = Purchase.objects.filter(user=request.user).select_related('product').order_by('-purchase_date')
    
    # Calculate totals
    total_quantity = sum(purchase.quantity for purchase in purchases)
    total_spent = sum(purchase.product.price * purchase.quantity for purchase in purchases)
    
    return render(request, 'store/purchase_history.html', {
        'purchases': purchases,
        'total_quantity': total_quantity,
        'total_spent': total_spent
    })


# Leave Feedback
@login_required
def leave_feedback(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = UserFeedbackForm(request.POST)
        if form.is_valid():
            try:
                # Save feedback
                feedback = form.save(commit=False)
                feedback.user = request.user
                feedback.product = product
                feedback.save()
                
                # Remove product from cart
                cart = request.session.get('cart', {})
                if str(product.id) in cart:
                    del cart[str(product.id)]
                    request.session['cart'] = cart
                    request.session.modified = True
                
                messages.success(request, "Thank you for your feedback!")
                return redirect('product_list')  # Or 'home' if you have a home page
                
            except Exception as e:
                logger.error(f"Feedback error: {str(e)}")
                messages.error(request, "Failed to save feedback")
        else:
            logger.error(f"Form errors: {form.errors}")
    else:
        form = UserFeedbackForm()
    
    return render(request, 'store/leave_feedback.html', {
        'form': form,
        'product': product
    })


# Cancel Purchase (Optional)
@login_required
def cancel_purchase(request, purchase_id):
    purchase = Purchase.objects.get(id=purchase_id)
    if purchase.user == request.user:
        purchase.delete()
        messages.success(request, 'Your purchase has been cancelled.')
    return redirect('view_cart')

@login_required
def custom_logout(request):
    logout(request)
    return redirect('login') 