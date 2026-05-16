from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from store.models import Book
from .models import Order, OrderItem


def _get_cart(request):
    return request.session.get('cart', {})


@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Savat bo‘sh. Avvalo kitob qo‘shing.')
        return redirect('home')

    items = []
    total = 0
    for book_id, quantity in cart.items():
        book = get_object_or_404(Book, id=book_id)
        cost = book.price * quantity
        total += cost
        items.append((book, quantity, cost))

    if request.method == 'POST':
        for book, quantity, cost in items:
            if book.stock < quantity:
                messages.warning(request, f'Kitob "{book.title}" yetarli omborda yo‘q. Iltimos, savatni tekshiring.')
                return redirect('cart_detail')

        order = Order.objects.create(user=request.user)
        for book, quantity, cost in items:
            OrderItem.objects.create(order=order, book=book, quantity=quantity, price=book.price)
            book.stock -= quantity
            book.save()

        request.session['cart'] = {}
        messages.success(request, 'Buyurtmangiz qabul qilindi. Rahmat!')
        return redirect('checkout_success')

    return render(request, 'checkout.html', {'items': items, 'total': total})


@login_required
def checkout_success(request):
    return render(request, 'checkout_success.html')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})
