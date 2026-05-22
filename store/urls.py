
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import BookViewSet, CategoryViewSet

router = DefaultRouter()
router.register('books', BookViewSet)
router.register('categories', CategoryViewSet)




urlpatterns = [
    path('', views.home, name='home'),
    path('book/<slug:slug>/', views.book_detail, name='book_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:book_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:book_id>/', views.decrease_quantity, name='decrease_quantity'),
    
    # Wishlist URLs
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:book_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/check/<int:book_id>/', views.is_in_wishlist, name='is_in_wishlist'),
    
    path('api/', include(router.urls)),
]
