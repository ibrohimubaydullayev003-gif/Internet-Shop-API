from django.urls import path

from .views import AdminOrderStatusView, CartAddView, CartRemoveView, CartView, CategoryDetailView, CategoryListCreateView, CheckoutView, LikeListView, LoginView, OrderListView, ProductCommentsView, ProductDetailView, ProductLikeView, ProductListCreateView, ProfileView, RegisterView, ChangePasswordView, LogoutView


urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/change-password/',    ChangePasswordView.as_view(),   name='change-password'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),

    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:product_id>/like/', ProductLikeView.as_view(), name='product-like'),
    path('products/<int:product_id>/comments/', ProductCommentsView.as_view(), name='product-comments'),

    path('likes/', LikeListView.as_view(), name='likes'),

    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartAddView.as_view(), name='cart-add'),
    path('cart/remove/', CartRemoveView.as_view(), name='cart-remove'),

    path('orders/checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderListView.as_view(), name='orders'),
    path('admin/orders/<int:order_id>/status/', AdminOrderStatusView.as_view(), name='admin-order-status'),
]
