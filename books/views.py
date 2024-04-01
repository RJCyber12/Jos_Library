# books/views.py
from django.views.generic import ListView, TemplateView
from .models import Book, Author

class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'  # Ensure this template exists

class AuthorListView(ListView):
    model = Author
    template_name = 'books/author_list.html'  # Ensure this template exists

class HomePageView(TemplateView):
    template_name = 'home.html'

class BookDetailView(DetailView):
    model = Book
    context_object_name = 'book'
    template_name = 'books/book_detail.html'