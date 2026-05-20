from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/<slug:slug>/', views.book_detail, name='book_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:book_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:book_id>/', views.decrease_quantity, name='decrease_quantity'),
]
