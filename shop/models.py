from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    ROLE_CUSTOMER = 'customer'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_CUSTOMER, 'Customer'),
        (ROLE_ADMIN, 'Admin'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)

    def save(self, *args, **kwargs):
        if self.email:
            self.username = self.email

        if self.is_superuser:
            self.role = self.ROLE_ADMIN
            self.is_staff = True
        elif self.role == self.ROLE_ADMIN:
            self.is_staff = True
        else:
            self.is_staff = False

        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f'{self.user.email} cart'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_product'),]

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'


class Order(models.Model):
    PENDING = 'pending'
    SHIPPING = 'shipping'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Kutilmoqda'),
        (SHIPPING, 'Yetkazilmoqda'),
        (COMPLETED, 'Bajarildi'),
        (CANCELLED, 'Bekor qilindi'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items',)
    quantity = models.PositiveIntegerField()
    price_at_that_time = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'Order #{self.order_id} item'


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_like'),]

    def __str__(self):
        return f'{self.user.email} -> {self.product.name}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name} - {self.rating}/5'
