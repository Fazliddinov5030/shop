from rest_framework import viewsets
from .models import Book, Category
from .serializers import BookSerializer, CategorySerializer



class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.filter(is_active=True).select_related('category')
    serializer_class = BookSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
