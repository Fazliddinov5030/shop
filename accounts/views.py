from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect

from .forms import CustomUserCreationForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Ro‘yxatdan o‘tish muvaffaqiyatli o‘tdi.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})
