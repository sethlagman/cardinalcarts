from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ProductForm
from .models import Profile, Product, CartItem, WishlistItem, OrderItem, Order, Transaction, UserActionLog, OrderActionLog, ProductActionLog
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
import random
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.urls import reverse

MAX_ATTEMPTS = 5
LOCKOUT_TIME = 300

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        auth_login(request, user)
        return redirect('dashboard')
    else:
        return render(request, 'verification_failed.html')

def send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_url = request.build_absolute_uri(
        reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
    )

    send_mail(
        subject='Verify Your Email - CardinalCarts',
        message=f'Hi {user.first_name},\n\nClick the link below to verify your account:\n\n{verification_url}\n\nThank you!',
        from_email='noreply@cardinalcarts.com',
        recipient_list=[user.email],
    )

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('adminUser')
        return redirect('dashboard')
    
    if 'login_attempts' not in request.session:
        request.session['login_attempts'] = 0
        request.session['last_attempt_time'] = str(timezone.now())

    last_attempt_time = timezone.datetime.fromisoformat(request.session['last_attempt_time'])

    if request.session['login_attempts'] >= MAX_ATTEMPTS:
        if timezone.now() - last_attempt_time < timedelta(seconds=LOCKOUT_TIME):
            time_left = timedelta(seconds=LOCKOUT_TIME) - (timezone.now() - last_attempt_time)
            minutes, seconds = divmod(time_left.seconds, 60)
            return render(request, 'login.html', {
                'error': f'Too many login attempts. Try again in {minutes}m {seconds}s'
            })
        else:
            request.session['login_attempts'] = 0

    context = {}

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            auth_user = authenticate(request, username=user.username, password=password)
            if auth_user:
                auth_login(request, auth_user)
                request.session['login_attempts'] = 0
                if auth_user.is_staff:
                    return redirect('adminInventory')
                return redirect('dashboard')
            else:
                request.session['login_attempts'] += 1
                request.session['last_attempt_time'] = str(timezone.now())
                context['error'] = f"Incorrect email or password. Attempts left: {MAX_ATTEMPTS - request.session['login_attempts']}"
        except User.DoesNotExist:
            request.session['login_attempts'] += 1
            request.session['last_attempt_time'] = str(timezone.now())
            context['error'] = f"Incorrect email or password. Attempts left: {MAX_ATTEMPTS - request.session['login_attempts']}"

    return render(request, 'login.html', context)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False  # 👈 prevent login until verified

            if form.cleaned_data['user_status'] == 'staff':
                user.is_staff = True
            user.save()

            Profile.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number'],
                user_status=form.cleaned_data['user_status']
            )

            send_verification_email(request, user)

            return render(request, 'verification_sent.html')  # Create this page
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    ready_orders = Order.objects.filter(status="Ready for Pickup", user=request.user)
    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    else:
        products = Product.objects.all()
    return render(request, 'dashboard.html', {'products': products, 'query': query, 'ready_orders': ready_orders})


@login_required
def view_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'viewOrder.html', {'product': product})


@login_required
def wishlist(request):
    query = request.GET.get("q")
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    ready_orders = Order.objects.filter(status="Ready for Pickup", user=request.user)
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items, 'ready_orders': ready_orders})


@login_required
def add_to_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)

    if not WishlistItem.objects.filter(user=request.user, product=product).exists():

        WishlistItem.objects.create(user=request.user, product=product)

    return redirect('wishlist')


@login_required
def remove_from_wishlist(request):
    if request.method == "POST":
        # Get selected items to remove
        selected_items = request.POST.getlist('remove_items')
        WishlistItem.objects.filter(id__in=selected_items).delete()
    return redirect('wishlist')

@login_required
def cart(request):
    query = request.GET.get("q")
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()

    ready_orders = Order.objects.filter(status="Ready for Pickup", user=request.user)
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, 'cart.html', {'cart_items': cart_items, 'ready_orders': ready_orders})


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return redirect('cart')


@login_required
def remove_from_cart(request):
    if request.method == "POST":
        item_ids = request.POST.getlist('remove_items')
        CartItem.objects.filter(id__in=item_ids, user=request.user).delete()
    return redirect('cart')


@login_required
def orderHistory(request):
    query = request.GET.get("q")
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    ready_orders = Order.objects.filter(status="Ready for Pickup", user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    for order in orders:
        total_price = 0
        for item in order.items.all():
            
            if item.total_price is None:
                item.total_price = item.product.price * item.quantity
            total_price += item.total_price
        order.total_price = total_price
        
    return render(request, 'orderHistory.html', {'orders': orders, 'ready_orders': ready_orders})


@login_required
def checkout(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        selected_items = CartItem.objects.filter(user=request.user)
        if not selected_items:
            return redirect('cart')
        
        order_number = f"{random.randint(10000000, 99999999)}"
        total_amount = sum(item.total_price for item in selected_items)

        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            status='Processing',
            payment_method=payment_method,
            total_amount=total_amount,
        )

        for item in selected_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            item.product.quantity -= item.quantity
            item.product.save()

        selected_items.delete()
        return redirect('orderHistory')

    return render(request, 'checkout.html')

@login_required
def viewOrder(request):
    return render(request, 'viewOrder.html')


#! Admin page

@staff_member_required
def adminInventory(request):
    products = Product.objects.all()
    return render(request, 'adminInventory.html', {'products': products})


@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()

            ProductActionLog.objects.create(
                admin=request.user,
                product_name=product.name,
                action='add',
                details=f"Added product: {product.name} (₱{product.price}, Qty: {product.quantity})"
            )

            return redirect('adminInventory')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@staff_member_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            old_name = product.name
            old_price = product.price
            old_quantity = product.quantity

            product = form.save()

            ProductActionLog.objects.create(
                admin=request.user,
                product_name=product.name,
                action='edit',
                details=f"Edited product: {old_name} (₱{old_price}, Qty: {old_quantity}) → {product.name} (₱{product.price}, Qty: {product.quantity})"
            )

            return redirect('adminInventory')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form})


@staff_member_required
def delete_product(request, product_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to delete this product.")
    
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_name = product.name
        details = f"Deleted product: {product_name} (₱{product.price}, Qty: {product.quantity})"
        print(product_name)
        print(details)
        ProductActionLog.objects.create(
            product_name=product_name,
            action='delete',
            admin=request.user,
            details=details
        )

        product.delete()
        return redirect('adminInventory')

    return HttpResponseForbidden("Invalid request method.")


@staff_member_required
def adminOrder(request):
    orders = Order.objects.all()
    
    for order in orders:
        total_price = 0
        for item in order.items.all():
            
            if item.total_price is None:
                item.total_price = item.product.price * item.quantity
            total_price += item.total_price
        order.total_price = total_price
        
    context = {
        'orders': orders,
    }
    return render(request, 'adminOrder.html', context)


@staff_member_required
def add_order(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        status = request.POST.get('status')
        quantities = request.POST.getlist('quantities')
        payment_method = request.POST.get('payment_method')
        pickup_date = request.POST.get('pickup_date')

        errors = []

        if len(first_name) < 2 or first_name.isspace():
            errors.append("First name must be at least 2 characters and not just spaces.")

        if len(last_name) < 2 or last_name.isspace():
            errors.append("Last name must be at least 2 characters and not just spaces.")

        for quantity in quantities:
            try:
                q = int(quantity)
                if q <= 0:
                    errors.append("Quantities must be positive integers.")
            except ValueError:
                errors.append("Quantities must be valid numbers.")

        if pickup_date:
            pickup = datetime.strptime(pickup_date, '%Y-%m-%d').date()
            if pickup < datetime.today().date():
                errors.append("Pickup date cannot be in the past.")

        if errors:
            order_number = f"{random.randint(10000000, 99999999)}"
            return render(request, 'addOrder.html', {
                'errors': errors,
                'order_number': order_number,
                'products': Product.objects.all()
            })

        user = User.objects.filter(first_name=first_name, last_name=last_name).first()

        if not user:
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            user_status = request.POST.get('user_status')

            user = User.objects.create_user(
                username=f"{first_name.lower()}{last_name.lower()}",
                first_name=first_name,
                last_name=last_name,
                email=email,
                password="defaultpassword"
            )

            Profile.objects.create(
                user=user,
                phone_number=phone_number,
                user_status=user_status
            )

        items = request.POST.getlist('items')
        quantities = request.POST.getlist('quantities')

        errors = []

        for item_id, quantity in zip(items, quantities):
            product = Product.objects.get(id=item_id)
            quantity = int(quantity)

            if quantity > product.quantity:
                errors.append(f"Not enough stock for {product.name}. Available: {product.quantity}, Requested: {quantity}")

        if errors:
            order_number = f"{random.randint(10000000, 99999999)}"
            return render(request, 'addOrder.html', {'errors': errors, 'order_number': order_number, 'products': Product.objects.all()})
                
        order_number = f"{random.randint(10000000, 99999999)}"
        order = Order.objects.create(
            user=user,
            order_number=order_number,
            status=status,
            payment_method=payment_method,
            pickup_date=pickup_date if pickup_date else None
        )

        total_amount = 0
        for item_id, quantity in zip(items, quantities):
            product = Product.objects.get(id=item_id)
            quantity = int(quantity)
            total_price = product.price * quantity
            total_amount += total_price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
                total_price=total_price
            )

            product.quantity -= quantity
            product.save()

        order.total_amount = total_amount
        order.save()

        OrderActionLog.objects.create(
            action_type='add',
            admin_user=request.user,
            details=f"Added order #{order.order_number} with status {order.status} and total amount {order.total_amount}"
        )

        return redirect('adminOrder')

    order_number = f"{random.randint(10000000, 99999999)}"
    products = Product.objects.all()

    return render(request, 'addOrder.html', {'order_number': order_number, 'products': products})


@staff_member_required
def edit_order(request):
    order = None
    error = None
    success = None

    if request.method == "POST":
        submit_btn = request.POST.get("submit_btn")

        if submit_btn == "Search Order":
            order_number = request.POST.get("order_number")
            try:
                order = Order.objects.get(order_number=order_number)
                order.total_amount = sum(item.product.price * item.quantity for item in order.items.all())
            except Order.DoesNotExist:
                error = "Order not found."

        elif submit_btn == "Update Order":
            order_number = request.POST.get("order_number")
            pickup_date = request.POST.get("pickup_date")
            status = request.POST.get("status")
            try:
                order = Order.objects.get(order_number=order_number)
                order.pickup_date = pickup_date
                order.status = status
                order.save()

                OrderActionLog.objects.create(
                    action_type='edit',
                    admin_user=request.user,
                    details=f"Updated order #{order.order_number} to status {order.status} and pickup date {pickup_date}"
                )

                if status == "Completed":

                    item_summary = ""
                    for item in order.items.all():
                        item_summary += f"{item.product.name} (x{item.quantity}) - ₱{item.price}\n"

                    Transaction.objects.create(
                        order_number=order.order_number,
                        user=order.user,
                        total_price=order.total_amount,
                        date_of_order=order.order_date,
                        items=item_summary.strip()
                    )

                    order.delete()

                success = "Order updated and moved to transactions."
                order = None
            except Order.DoesNotExist:
                error = "Order not found."

    return render(request, 'editOrder.html', {'order': order, 'error': error, 'success': success})


@staff_member_required
def delete_order(request):
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        
        try:
            order = Order.objects.get(order_number=order_number)

            OrderActionLog.objects.create(
                action_type='delete',
                admin_user=request.user,
                details=f"Deleted order #{order.order_number}"
            )

            order.delete()
            messages.success(request, f"Order {order_number} has been successfully deleted.")
            return redirect('adminOrder')
        except Order.DoesNotExist:
            messages.error(request, f"Order {order_number} does not exist.")
    
    return render(request, 'deleteOrder.html')


@staff_member_required
def adminTransaction(request):
    transactions = Transaction.objects.all().order_by('-date_of_order')
    return render(request, 'adminTransaction.html', {'transactions': transactions})


@staff_member_required
def adminUser(request):
    users = User.objects.all()
    return render(request, 'adminUser.html', {'users': users})


@staff_member_required
def add_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)

            user_status = form.cleaned_data['user_status']
            if user_status == 'staff':
                user.is_staff = True

            user.save()

            Profile.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number'],
                user_status=user_status,
            )

            UserActionLog.objects.create(
                action_type='add',
                admin_user=request.user,
                details=f"Added user {user.first_name} {user.last_name}, status: {user_status}"
            )

            return redirect('adminUser')
    else:
        form = RegisterForm()

    return render(request, 'add_user.html', {'form': form})


@staff_member_required
def edit_user(request):
    if request.method == 'POST':
        user_id = request.POST['user_id']
        user = get_object_or_404(User, id=user_id)
        
        old_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }

        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        user.save()

        UserActionLog.objects.create(
            action_type='edit',
            admin_user=request.user,
            details=f"Edited user {user.first_name} {user.last_name} (changes: {old_data})"
        )

        return redirect('adminUser')
    
    return render(request, 'edit_user.html')


@staff_member_required
def delete_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        try:
            user = User.objects.get(first_name=first_name, last_name=last_name)

            UserActionLog.objects.create(
                action_type='delete',
                admin_user=request.user,
                details=f"Deleted user {user.first_name} {user.last_name}"
            )

            user.delete()
        except User.DoesNotExist:
            return HttpResponseForbidden("User not found")
        return redirect('adminUser')

    return render(request, 'delete_user.html')


@staff_member_required
def user_log(request):
    logs = UserActionLog.objects.all().order_by('-timestamp')
    return render(request, 'user_action_log.html', {'logs': logs})


@staff_member_required
def order_action_log(request):
    logs = OrderActionLog.objects.all().order_by('-timestamp')
    return render(request, 'order_action_log.html', {'logs': logs})


@staff_member_required
def product_action_log(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only admins can view logs.")

    logs = ProductActionLog.objects.all().order_by('-timestamp')
    return render(request, 'product_action_log.html', {'logs': logs})
