from django.contrib import admin

from .models import Book, Category, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'price', 'stock', 'is_active')
    list_filter = ('category', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'author')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'book_count')
    search_fields = ('user__username',)
    filter_horizontal = ('books',)

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = 'Books in Wishlist'
