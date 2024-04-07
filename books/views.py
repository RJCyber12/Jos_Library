# books/views.py
from django.views.generic import ListView, TemplateView, DetailView
from .models import Book, Author, Shelf
from django.shortcuts import render, redirect
from django.views import View, generic
import requests, logging
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile


class HomePageView(TemplateView):
    template_name = 'books/home.html'


logger = logging.getLogger(__name__)

class BookListView(View):
    template_name = 'books/book_list.html'

    def get(self, request):
        context = {'books': [], 'error': None}
        page = int(request.GET.get('page', 1))
        items_per_page = 20
        start = (page - 1) * items_per_page  # Calculate start offset
        query = request.GET.get('query', '')  # Get the search query
        data = {}  # Initialize data as an empty dictionary

        try:
            url = f"https://openlibrary.org/search.json?q={query}&start={start}&limit={items_per_page}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()  # Now data will be assigned with API response or remain empty

             #Process each book to include openlibrary_id
            books_processed = []
            for book in data.get('docs', []):
                book['openlibrary_id'] = book['key'].split('/')[-1]
                books_processed.append(book)


            context['books'] = books_processed
            context['numFound'] = data.get('numFound', 0)
            context['has_previous'] = page > 1
            context['has_next'] = start + len(context['books']) < context['numFound']
            context['next_page'] = page + 1
            context['previous_page'] = page - 1
        except requests.RequestException as e:
            context['error'] = str(e)

        # Since data is initialized as {}, using .get() will safely return default values if not set
        context['query'] = query  # Include the search query in context for use in the template

        return render(request, self.template_name, context)



class AuthorListView(View):
    template_name = 'books/author_list.html'

    def get(self, request):
        context = {'authors': []}
        query = request.GET.get('query')

        if query:
            url = f"https://openlibrary.org/search/authors.json?q={query}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                context['authors'] = data['docs']  # Adjust depending on the structure of the response

        return render(request, self.template_name, context)



class BookDetailView(View):
    template_name = 'books/book_detail.html'

    def get(self, request, openlibrary_id):
        context = {'book': None, 'error': None}

        try:
            # Fetch the book details
            book_url = f"https://openlibrary.org/works/{openlibrary_id}.json"
            book_response = requests.get(book_url)
            book_data = book_response.json()

            author_name = "Unknown Author"
            if 'authors' in book_data and book_data['authors']:
                # Assuming the first author as the representative author
                author_key = book_data['authors'][0]['author']['key']
                author_url = f"https://openlibrary.org{author_key}.json"
                author_response = requests.get(author_url)
                if author_response.status_code == 200:
                    author_data = author_response.json()
                    author_name = author_data.get('name', "Unknown Author")

            book_detail = {
                'title': book_data.get('title', 'No title available'),
                'openlibrary_id': openlibrary_id,
                'author_name': author_name,
                'publish_date': book_data.get('created', {}).get('value', 'No publish date available'),
                'cover_id': book_data.get('covers', [])[0] if 'covers' in book_data and book_data['covers'] else None,
            }

            context['book'] = book_detail

        except requests.RequestException as e:
            context['error'] = f"Request error: {e}"
        except KeyError as e:
            context['error'] = f"Data parsing error: Missing key {e}"

        return render(request, self.template_name, context)



def get_or_create_book_from_openlibrary(openlibrary_id):
    # Try to get the book from the database first
    try:
        return Book.objects.get(openlibrary_id=openlibrary_id), False
    except Book.DoesNotExist:
        # If the book is not found, fetch its details from Open Library
        url = f"https://openlibrary.org/works/{openlibrary_id}.json"
        response = requests.get(url)
        if response.status_code == 200:
            book_data = response.json()
            # Extract author names and create Author instances if necessary
            author_names = [author['name'] for author in book_data.get('authors', [])]
            authors = []
            for name in author_names:
                author, _ = Author.objects.get_or_create(name=name)
                authors.append(author)
            
            # Create a new Book instance
            book = Book(
                openlibrary_id=openlibrary_id,
                title=book_data.get('title'),
                # Assuming you want to link the first author for simplicity
                author=authors[0] if authors else None,
            )
            
            # Optionally, fetch and save the cover image
            cover_id = book_data.get('covers', [])[0] if book_data.get('covers') else None
            if cover_id:
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                cover_response = requests.get(cover_url)
                if cover_response.status_code == 200:
                    book.cover_image.save(f"{openlibrary_id}.jpg", ContentFile(cover_response.content), save=False)
            
            book.save()
            
            # If there are multiple authors, add them to the book's authors field
            if len(authors) > 1:
                for author in authors[1:]:
                    book.authors.add(author)
                book.save()
            
            return book, True
        else:
            raise Exception("Could not fetch book from Open Library")

@require_POST
def add_to_shelf(request, book_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Fetch or create the book instance
    # Assuming you have a function to fetch or create a book from OpenLibrary API by ID
    book, created = get_or_create_book_from_openlibrary(book_id)
    
    # Get or create the user's shelf (assuming one shelf per user for simplicity)
    shelf, created = Shelf.objects.get_or_create(user=request.user)
    
    # Add the book to the user's shelf
    shelf.books.add(book)
    
    return redirect('book-list')  # Redirect back to the book list page



#Registration views
class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'books/signup.html'


def user_dashboard(request):
    if request.user.is_authenticated:
        # Assuming each user has only one shelf for simplicity
        shelf, created = Shelf.objects.get_or_create(user=request.user)
        return render(request, 'books/user_dashboard.html', {'shelf': shelf})
    else:
        # Redirect to login page or show an error
        return redirect('login')