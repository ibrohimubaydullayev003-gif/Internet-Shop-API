from django.contrib.auth import authenticate
from django.db import transaction
from django_filters import rest_framework 
from rest_framework import generics, status, serializers 
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem, Category, Comment, Like, Order, OrderItem, Product
from .serializers import CartAddSerializer, CartRemoveSerializer, CartSerializer, CategorySerializer, CheckoutSerializer, CommentSerializer, LikeSerializer, LoginSerializer, OrderSerializer, OrderStatusSerializer, ProductSerializer, RegisterSerializer, UserSerializer



class ProductFilter(rest_framework.FilterSet):
    category = rest_framework.CharFilter(field_name='category__slug', lookup_expr='iexact')
    min_price = rest_framework.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = rest_framework.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price']


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'message': 'Ro\'yxatdan o\'tish muvaffaqiyatli.',
                'token': token.key,
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {'detail': 'Email yoki password noto\'g\'ri.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'user': UserSerializer(user).data,
            }
        )


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related('category').all().order_by('-created_at')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]


class ProductLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = generics.get_object_or_404(Product, id=product_id)
        like = Like.objects.filter(user=request.user, product=product).first()

        if like:
            like.delete()
            return Response({'liked': False, 'message': 'Like olib tashlandi.'})

        Like.objects.create(user=request.user, product=product)
        return Response({'liked': True, 'message': 'Like bosildi.'}, status=status.HTTP_201_CREATED)


class LikeListView(generics.ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Like.objects.filter(user=self.request.user).select_related('product').order_by('-created_at')


class ProductCommentsView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(product_id=self.kwargs['product_id']).select_related('user').order_by('-created_at')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        product = generics.get_object_or_404(Product, id=self.kwargs['product_id'])
        serializer.save(user=self.request.user, product=product)


class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartAddView(generics.GenericAPIView):
    serializer_class = CartAddSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        product = generics.get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item = CartItem.objects.filter(cart=cart, product=product).first()

        old_quantity = item.quantity if item else 0
        new_quantity = old_quantity + quantity

        if new_quantity > product.stock:
            return Response(
                {'detail': f'Sklad qoldig\'i yetarli emas. Qoldiq: {product.stock}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if item:
            item.quantity = new_quantity
            item.save(update_fields=['quantity'])
        else:
            CartItem.objects.create(cart=cart, product=product, quantity=quantity)

        return Response({'message': 'Mahsulot savatga qo\'shildi.'}, status=status.HTTP_201_CREATED)


class CartRemoveView(generics.GenericAPIView):
    serializer_class = CartRemoveSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = generics.get_object_or_404(Cart, user=request.user)
        product_id = serializer.validated_data['product_id']
        item = CartItem.objects.filter(cart=cart, product_id=product_id).first()

        if not item:
            return Response(
                {'detail': 'Bu mahsulot savatda yo\'q.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        item.delete()
        return Response({'message': 'Mahsulot savatdan o\'chirildi.'})


class CheckoutView(generics.GenericAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = generics.get_object_or_404(Cart.objects.select_for_update(), user=request.user)
        cart_items = list(cart.items.all())

        if not cart_items:
            return Response(
                {'detail': 'Savat bo\'sh.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.create(
            user=request.user,
            shipping_address=serializer.validated_data['shipping_address'],
        )

        total_price = 0

        for cart_item in cart_items:
            product = Product.objects.select_for_update().get(id=cart_item.product_id)

            if cart_item.quantity > product.stock:
                raise serializers.ValidationError(
                    f'{product.name} uchun sklad qoldig\'i yetarli emas.'
                )

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                price_at_that_time=product.price,
            )

            total_price += product.price * cart_item.quantity
            product.stock -= cart_item.quantity
            product.save(update_fields=['stock'])

        order.total_price = total_price
        order.save(update_fields=['total_price'])
        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product').order_by('-created_at')


class AdminOrderStatusView(generics.GenericAPIView):
    serializer_class = OrderStatusSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, order_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = generics.get_object_or_404(Order, id=order_id)
        order.status = serializer.validated_data['status']
        order.save(update_fields=['status'])

        return Response(OrderSerializer(order).data)
