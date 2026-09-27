from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Cart, CartItem, Category, Comment, Like, Order, OrderItem, Product, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Qo\'shimcha', {'fields': ('phone', 'role')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Qo\'shimcha', {'fields': ('email', 'phone', 'role')}),
    )
    search_fields = ('username', 'email', 'phone')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'parent')
    search_fields = ('name', 'slug')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__email',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price_at_that_time')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'created_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'rating', 'created_at')
    list_filter = ('rating',)
