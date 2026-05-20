from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Book, Category


def _get_cart(request):
    return request.session.setdefault('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def home(request):
    category_slug = request.GET.get('category')
    query = request.GET.get('q', '')
    categories = Category.objects.all()
    books = Book.objects.filter(is_active=True)

    if category_slug:
        books = books.filter(category__slug=category_slug)

    if query:
        books = books.filter(title__icontains=query) | books.filter(author__icontains=query)

    return render(request, 'home.html', {
        'books': books,
        'categories': categories,
        'selected_category': category_slug,
        'query': query,
    })


def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug, is_active=True)
    return render(request, 'book_detail.html', {'book': book})


def cart_detail(request):
    cart = _get_cart(request)
    items = []
    total = 0
    for book_id, quantity in cart.items():
        book = get_object_or_404(Book, id=book_id)
        cost = book.price * quantity
        total += cost
        items.append({'book': book, 'quantity': quantity, 'cost': cost})

    return render(request, 'cart.html', {'items': items, 'total': total})


def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id, is_active=True)
    cart = _get_cart(request)
    cart[str(book.id)] = cart.get(str(book.id), 0) + 1
    _save_cart(request, cart)
    # Prepare cart count
    try:
        total_count = sum(int(v) for v in cart.values())
    except Exception:
        total_count = len(cart)

    # If called via AJAX, return JSON so frontend can update without redirect
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': total_count, 'book_title': book.title})

    messages.success(request, f'"{book.title}" savatga qo‘shildi.')
    return redirect('cart_detail')




@require_POST
def remove_from_cart(request, book_id):
    cart = _get_cart(request)
    if str(book_id) in cart:
        cart.pop(str(book_id))
        _save_cart(request, cart)
        messages.success(request, 'Mahsulot savatdan o\'chirildi.')
    return redirect('cart_detail')

@require_POST
def increase_quantity(request, book_id):
    book = get_object_or_404(Book, id=book_id, is_active=True)
    cart = _get_cart(request)
    if str(book_id) in cart:
        # Check if increasing would exceed stock
        if cart[str(book_id)] < book.stock:
            cart[str(book_id)] += 1
            _save_cart(request, cart)
        else:
            messages.warning(request, f'"{book.title}" uchun yetarli ombor yo\'q.')
    return redirect('cart_detail')


@require_POST
def decrease_quantity(request, book_id):
    book = get_object_or_404(Book, id=book_id, is_active=True)
    cart = _get_cart(request)
    if str(book_id) in cart:
        if cart[str(book_id)] > 1:
            cart[str(book_id)] -= 1
            _save_cart(request, cart)
        else:
            # If quantity would be 0, remove from cart
            cart.pop(str(book_id))
            _save_cart(request, cart)
            messages.success(request, 'Mahsulot savatdan o\'chirildi.')
    return redirect('cart_detail')