from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Book, Category, Wishlist


def _get_cart(request):
    return request.session.setdefault('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def home(request):
    category_slug = request.GET.get('category')
    query = request.GET.get('q', '')
    categories = Category.objects.all()
    books = Book.objects.filter(is_active=True).select_related('category')

    if category_slug:
        books = books.filter(category__slug=category_slug)

    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query)).distinct()

    paginator = Paginator(books, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'home.html', {
        'books': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'query': query,
    })

def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug, is_active=True)
    return render(request, 'book_detail.html', {'book': book})


def cart_detail(request):
    cart = _get_cart(request)
    if not cart:
        return render(request, 'cart.html', {'items': [], 'total': 0})

    books = Book.objects.filter(id__in=cart.keys())
    books_dict = {str(b.id): b for b in books}

    items = []
    total = 0
    for book_id, quantity in cart.items():
        book = books_dict.get(book_id)
        if not book:
            continue
        cost = book.price * quantity
        total += cost
        items.append({'book': book, 'quantity': quantity, 'cost': cost})

    return render(request, 'cart.html', {'items': items, 'total': total})


@require_POST
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id, is_active=True)
    cart = _get_cart(request)
    current_quantity = cart.get(str(book.id), 0)

    if current_quantity + 1 > book.stock:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Omborda yetarli emas'})
        messages.warning(request, f'"{book.title}" omborda yetarli emas.')
        return redirect('cart_detail')

    cart[str(book.id)] = current_quantity + 1
    _save_cart(request, cart)

    try:
        total_count = sum(int(v) for v in cart.values())
    except Exception:
        total_count = len(cart)

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


# Wishlist views
@login_required
def wishlist_view(request):
    """Display user's wishlist"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    books = wishlist.books.all()
    
    return render(request, 'wishlist.html', {
        'wishlist_items': books,
        'wishlist': wishlist
    })


@login_required
@require_POST
def add_to_wishlist(request, book_id):
    """Add book to wishlist"""
    book = get_object_or_404(Book, id=book_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if book not in wishlist.books.all():
        wishlist.books.add(book)
        message = f'"{book.title}" sevimlilar ro\'yxatiga qo\'shildi.'
    else:
        message = f'"{book.title}" allaqachon sevimlilar ro\'yxatida.'
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'is_in_wishlist': True
        })
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
@require_POST
def toggle_wishlist(request, book_id):
    """Kitobni sevimlilarga qo'shish yoki olib tashlash (Toggle)"""
    book = get_object_or_404(Book, id=book_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if book in wishlist.books.all():
        wishlist.books.remove(book)
        added = False
        message = f'"{book.title}" sevimlilar ro\'yxatidan olib tashlandi.'
    else:
        wishlist.books.add(book)
        added = True
        message = f'"{book.title}" sevimlilar ro\'yxatiga qo\'shildi.'
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'added': added,
            'message': message,
            'wishlist_count': wishlist.books.count()
        })
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'wishlist_view'))

@login_required
@require_POST
def remove_from_wishlist(request, book_id):
    """Remove book from wishlist"""
    book = get_object_or_404(Book, id=book_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if book in wishlist.books.all():
        wishlist.books.remove(book)
        message = f'"{book.title}" sevimlilar ro\'yxatidan o\'chirildi.'
    else:
        message = f'"{book.title}" sevimlilar ro\'yxatida mavjud emas.'
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'is_in_wishlist': False
        })
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'wishlist_view'))


@login_required
def is_in_wishlist(request, book_id):
    """Check if book is in user's wishlist (AJAX)"""
    book = get_object_or_404(Book, id=book_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    is_wishlisted = book in wishlist.books.all()
    
    return JsonResponse({
        'is_in_wishlist': is_wishlisted
    })