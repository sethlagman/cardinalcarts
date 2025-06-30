from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    USER_STATUS_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    user_status = models.CharField(max_length=10, choices=USER_STATUS_CHOICES)

    def __str__(self):
        return self.user.username
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    category = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return self.name
    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.price * self.quantity
    
class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Wishlist item for {self.user.username} - {self.product.name}"
    
class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Processing', 'Processing'),
        ('Ready for Pickup', 'Ready for Pickup'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Processing')
    payment_method = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    pickup_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.order_number} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Calculate the total price (price * quantity)
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
    
class Transaction(models.Model):
    order_number = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.TextField(default="No items")
    date_of_order = models.DateField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Transaction {self.order_number}"

class UserActionLog(models.Model):
    ACTION_CHOICES = [
        ('add', 'Add'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
    ]

    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.action_type.capitalize()} action on {self.target_user.get_full_name()} by {self.admin_user.get_full_name()}"
    
class OrderActionLog(models.Model):
    ACTION_CHOICES = [
        ('add', 'Add'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
    ]

    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_action_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.action_type.capitalize()} action on Order #{self.order.order_number} by {self.admin_user.get_full_name()}"
    
class ProductActionLog(models.Model):
    ACTION_CHOICES = [
        ('add', 'Add'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
    ]
    
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.product_name} - {self.action} by {self.admin}"
