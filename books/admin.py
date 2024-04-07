# books/admin.py
from django.contrib import admin
from .models import Author, Book, CustomUser, Shelf


admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Shelf)
admin.site.register(CustomUser)
