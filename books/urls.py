# books/urls.py
from django.urls import path
from .views import BookListView, AuthorListView, BookDetailView, HomePageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('books/', BookListView.as_view(), name='book-list'),
    path('authors/', AuthorListView.as_view(), name='author-list'),
    path('books/<str:openlibrary_id>/', BookDetailView.as_view(), name='book-detail'),

]
