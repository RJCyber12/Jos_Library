# books/views.py
from django.views.generic import ListView, TemplateView, DetailView, UpdateView, DeleteView
from .models import Book, Author, Shelf
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View, generic
import requests, logging
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseNotFound
from django.contrib import messages
from django.conf import settings
import os




class HomePageView(TemplateView):
    template_name = 'books/home.html'


logger = logging.getLogger(__name__)

class BookListView(View):
    template_name = 'books/book_list.html'

    def get(self, request):
        context = {'books': [], 'error': None}
        page = int(request.GET.get('page', 1))
        items_per_page = 20
        start = (page - 1) * items_per_page  #calculate start offset
        query = request.GET.get('query', '')  #get the search query
        data = {}  #init data empty dict

        try:
            url = f"https://openlibrary.org/search.json?q={query}&start={start}&limit={items_per_page}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()  #data to api response or empty

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

    
        context['query'] = query  #search query in context for template

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
                context['authors'] = data['docs']

        return render(request, self.template_name, context)



class BookDetailView(View):
    template_name = 'books/book_detail.html'

    def get(self, request, openlibrary_id):
        context = {'book': None, 'error': None}

        try:
            #fetch the book details
            book_url = f"https://openlibrary.org/works/{openlibrary_id}.json"
            book_response = requests.get(book_url)
            book_data = book_response.json()

            author_name = "Unknown Author"
            if 'authors' in book_data and book_data['authors']:
                #first author
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


class BookUpdateView(UpdateView):
    model = Book
    fields = ['title', 'authors', 'cover_image']
    template_name = 'books/edit_book.html'
    success_url = reverse_lazy('user-dashboard')



class BookDeleteView(DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('user-dashboard')  # Redirect back to the dashboard after deletion

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Delete the cover image file
        if self.object.cover_image:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.object.cover_image.name))
        return super(BookDeleteView, self).delete(request, *args, **kwargs)
    

@login_required
def add_to_shelf(request, openlibrary_id):
    print(f"Request: {request}, OpenLibrary ID: {openlibrary_id}")  # Debug print

    try:
        book_data_response = requests.get(f'https://openlibrary.org/works/{openlibrary_id}.json')
        book_data_response.raise_for_status()  # This will raise an HTTPError if the status is 4xx or 5xx
        book_data = book_data_response.json()

        title = book_data.get('title', 'No Title Available')
        authors_data = book_data.get('authors', [])
        
        author_objs = []
        for author_ref in authors_data:
            author_id = author_ref.get('author', {}).get('key').split('/')[-1]
            author_response = requests.get(f'https://openlibrary.org/authors/{author_id}.json')
            if author_response.status_code == 200:
                author_info = author_response.json()
                author_name = author_info.get('name', 'Unknown Author')
                author, _ = Author.objects.get_or_create(name=author_name)
                author_objs.append(author)
                
        if not author_objs:  # Ensure there's at least one author, even if it's an unknown one
            default_author, _ = Author.objects.get_or_create(name='Unknown Author')
            author_objs.append(default_author)

        book, created = Book.objects.get_or_create(
            openlibrary_id=openlibrary_id,
            defaults={'title': title}
        )
        
        # Assign authors whether the book was just created or already existed
        book.authors.set(author_objs)

        # Handle cover image after ensuring the book exists
        cover_id = book_data.get('covers', [None])[0]
        if cover_id:
            cover_image_url = f"http://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            cover_response = requests.get(cover_image_url)
            if cover_response.status_code == 200 and cover_response.content:
                cover_image_content = ContentFile(cover_response.content)
                cover_image_filename = f'{openlibrary_id}.jpg'
                book.cover_image.save(cover_image_filename, cover_image_content, save=True)
                
        shelf, _ = Shelf.objects.get_or_create(user=request.user)
        shelf.books.add(book)
        # Book added successfully
        messages.success(request, "Book successfully added to shelf.")
    except Exception as e:
        # If there is any error, print the error and set a generic error message
        print(f"An unexpected error occurred: {e}")
        messages.error(request, "An error occurred while adding the book. Please try again.")
    
    # Redirect to the user dashboard in both success and error scenarios
    return redirect('user-dashboard')  # Ensure you have a URL named 'user_dashboard' in your urls.py


#Registration views
class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'books/signup.html'


@login_required
def user_dashboard(request):
    if request.user.is_authenticated:
        shelf, created = Shelf.objects.get_or_create(user=request.user)
        # Ensure books are being passed to the template
        return render(request, 'books/user_dashboard.html', {'shelf': shelf})
    else:
        return redirect('login')