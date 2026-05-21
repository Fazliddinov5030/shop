from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm, UserProfileForm, CustomPasswordChangeForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Ro\'yxatdan o\'tish muvaffaqiyatli o\'tdi.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil yangilandi.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Get user statistics
    from django.db.models import Sum, Count, F, DecimalField
    from django.db.models.functions import Coalesce
    from orders.models import Order, OrderItem
    
    # Get completed orders
    completed_orders = Order.objects.filter(user=request.user, status='completed')
    
    # Calculate total spent using F expressions
    total_spent_result = OrderItem.objects.filter(
        order__user=request.user, 
        order__status='completed'
    ).aggregate(
        total=Coalesce(
            Sum(F('price') * F('quantity'), output_field=DecimalField()),
            0,
            output_field=DecimalField()
        )
    )
    total_spent = total_spent_result['total'] or 0
    
    # Get bought books with details
    bought_books = []
    for order in completed_orders.prefetch_related('items__book').order_by('-created_at'):
        for item in order.items.all():
            bought_books.append({
                'book': item.book,
                'quantity': item.quantity,
                'price': item.price,
                'order_date': order.created_at
            })
    
    # Get unique books count
    unique_books_count = len(set(item['book'].id for item in bought_books))
    total_books_count = sum(item['quantity'] for item in bought_books)
    
    context = {
        'form': form,
        'total_spent': total_spent,
        'unique_books_count': unique_books_count,
        'total_books_count': total_books_count,
        'bought_books': bought_books[:6],  # Show recent 6 books
        'member_since': request.user.date_joined
    }
    
    return render(request, 'accounts/profile.html', context)


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        messages.success(self.request, 'Parol muvaffaqiyatli o\'zgartirildi.')
        return super().form_valid(form)


def password_change_done(request):
    return render(request, 'accounts/password_change_done.html')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')


def password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')
