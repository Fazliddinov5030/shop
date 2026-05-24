from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.conf import settings

from store.models import Book
from .models import Order, OrderItem


def _get_cart(request):
    return request.session.get('cart', {})


@login_required
@transaction.atomic
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, "Savat bo'sh. Avvalo kitob qo'shing.")
        return redirect('home')

    # Barcha kitoblarni BITTA SQL bilan olish (N+1 hal qilindi)
    book_ids = list(cart.keys())
    books = Book.objects.select_for_update().filter(id__in=book_ids)
    books_dict = {str(b.id): b for b in books}

    if request.method == 'POST':
        # Stock tekshiruv — lock ostida (race condition hal qilindi)
        for book_id, quantity in cart.items():
            book = books_dict.get(book_id)
            if not book or book.stock < quantity:
                messages.warning(request, f'Kitob "{book.title}" yetarli omborda yo\'q.')
                return redirect('cart_detail')

        order = Order.objects.create(user=request.user)
        for book_id, quantity in cart.items():
            book = books_dict[book_id]
            OrderItem.objects.create(
                order=order,
                book=book,
                quantity=quantity,
                price=book.price
            )
            # F() — atomik minus, race condition yo'q
            Book.objects.filter(id=book.id).update(stock=F('stock') - quantity)


        email_items = [
            {'book': books_dict[book_id], 'quantity': quantity, 'price': books_dict[book_id].price}
            for book_id, quantity in cart.items()
        ]
        subject = f'BookHub — Buyurtma #{order.id} qabul qilindi'
        message = render_to_string('email_confirmation.html', {
            'order': order,
            'items': email_items,
        })

        from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER or 'no-reply@bookhub.uz'
        if request.user.email:
            try:
                send_mail(
                    subject,
                    message,
                    from_email,
                    [request.user.email],
                    fail_silently=False,
                )
            except BadHeaderError:
                messages.warning(request, 'Email sarlavhasida xatolik bor. Iltimos keyinroq tekshiring.')
            except Exception:
                messages.warning(request, 'Email yuborishda xatolik yuz berdi. Buyurtma qabul qilindi, lekin email tasdiqi yuborilmadi.')
        else:
            messages.warning(request, 'Sizning profildagi email manzilingiz mavjud emas. Email tasdiqlash yuborilmadi.')

        request.session['cart'] = {}
        messages.success(request, 'Buyurtmangiz qabul qilindi. Rahmat!')
        return redirect('checkout_success')

    # GET — sahifani ko'rsatish uchun items ro'yxat yasaymiz
    items = []
    total = 0
    for book_id, quantity in cart.items():
        book = books_dict.get(book_id)
        if not book:
            continue
        cost = book.price * quantity
        total += cost
        items.append((book, quantity, cost))

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