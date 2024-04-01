# books/urls.py
from django.urls import path
from .views import BookListView, AuthorListView

urlpatterns = [
    path('', BookListView.as_view(), name='book-list'),
    path('authors/', AuthorListView.as_view(), name='author-list'),
]
