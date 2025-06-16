from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from base.models import (
    Product, Order, OrderItem, Transaction, Profile,
    ProductActionLog, OrderActionLog, UserActionLog,
    CartItem, WishlistItem
)
from django.utils import timezone

#! USER TEST

class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.password = "pass12345"
        self.user = User.objects.create_user(username="testuser", email="test@email.com", password=self.password)
        self.staff_user = User.objects.create_user(username="admin", email="admin@email.com", password=self.password, is_staff=True)

        Profile.objects.create(user=self.user, phone_number='1234567890', user_status='customer')
        Profile.objects.create(user=self.staff_user, phone_number='1234567890', user_status='staff')

        self.product = Product.objects.create(name="Pencil", description="HB Pencil", price=5.0, quantity=100)

    def test_login_redirect_dashboard(self):
        self.client.login(username="testuser", password=self.password)
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("dashboard"))

    def test_login_redirect_admin(self):
        self.client.login(username="admin", password=self.password)
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("adminUser"))

    def test_register_user(self):
        response = self.client.post(reverse("register"), {
            "username": "newuser",
            "email": "new@email.com",
            "password": "newpass123",
            "phone_number": "987654321",
            "user_status": "customer"
        })
        self.assertEqual(response.status_code, 200)

    def test_dashboard_access(self):
        self.client.login(username="testuser", password=self.password)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")

    def test_add_to_wishlist(self):
        self.client.login(username="testuser", password=self.password)
        response = self.client.get(reverse("add_to_wishlist", args=[self.product.id]))
        self.assertRedirects(response, reverse("wishlist"))
        self.assertEqual(WishlistItem.objects.count(), 1)

    def test_remove_from_wishlist(self):
        self.client.login(username="testuser", password=self.password)
        WishlistItem.objects.create(user=self.user, product=self.product)
        item_id = WishlistItem.objects.first().id
        response = self.client.post(reverse("remove_from_wishlist"), {
            "remove_items": [item_id]
        })
        self.assertRedirects(response, reverse("wishlist"))
        self.assertEqual(WishlistItem.objects.count(), 0)

    def test_add_to_cart(self):
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(reverse("add_to_cart", args=[self.product.id]), {
            "quantity": 2
        })
        self.assertRedirects(response, reverse("cart"))
        self.assertEqual(CartItem.objects.count(), 1)
        cart_item = CartItem.objects.first()
        self.assertEqual(cart_item.quantity, 2)

    def test_remove_from_cart(self):
        self.client.login(username="testuser", password=self.password)
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        cart_item_id = CartItem.objects.first().id
        response = self.client.post(reverse("remove_from_cart"), {
            "remove_items": [cart_item_id]
        })
        self.assertRedirects(response, reverse("cart"))
        self.assertEqual(CartItem.objects.count(), 0)

    def test_checkout_process(self):
        self.client.login(username="testuser", password=self.password)
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)

        response = self.client.post(reverse("checkout"), {
            "payment_method": "pay-on-pickup"
        })
        self.assertRedirects(response, reverse("orderHistory"))
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

        product = Product.objects.get(id=self.product.id)
        self.assertEqual(product.quantity, 98)

    def test_order_history_view(self):
        self.client.login(username="testuser", password=self.password)
        order = Order.objects.create(user=self.user, status="Ready for Pickup", order_number="12345678", payment_method="pay-on-pickup", total_amount=0)
        OrderItem.objects.create(order=order, product=self.product, quantity=2, price=self.product.price)
        response = self.client.get(reverse("orderHistory"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "12345678")

    def test_view_order_detail(self):
        self.client.login(username="testuser", password=self.password)
        response = self.client.get(reverse("view_order", args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pencil")

#! ADMIN TEST

class ViewTestsAdmin(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin', password='adminpass', is_staff=True
        )
        self.product = Product.objects.create(
            name='Sample Product', price=100, quantity=10, description="Test"
        )

    def test_admin_inventory_view(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('adminInventory'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_add_product_view(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('add_product'), {
            'name': 'New Product',
            'price': 150,
            'quantity': 5,
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, 302)  # redirect to adminInventory
        self.assertTrue(Product.objects.filter(name='New Product').exists())
        self.assertTrue(ProductActionLog.objects.filter(action='add').exists())

    def test_edit_product_view(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('edit_product', args=[self.product.id]), {
            'name': 'Updated Product',
            'price': 200,
            'quantity': 8,
            'description': 'Updated desc'
        })
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')
        self.assertTrue(ProductActionLog.objects.filter(action='edit').exists())

    def test_delete_product_view(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('delete_product', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
        self.assertTrue(ProductActionLog.objects.filter(action='delete').exists())

    def test_admin_order_page(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('adminOrder'))
        self.assertEqual(response.status_code, 200)

    def test_add_user_view(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('add_user'), {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@example.com',
            'password': '12345678',
            'phone_number': '09123456789',
            'user_status': 'student'
        })

        if response.status_code != 302:
            print("Form errors:", response.context['form'].errors)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Profile.objects.filter(user__username='newuser').exists())
        self.assertTrue(UserActionLog.objects.filter(action_type='add').exists())
