# books/views.py
from django.views.generic import ListView, TemplateView, DetailView
from .models import Book, Author
from django.shortcuts import render
from django.views import View
import requests, logging


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

            context['books'] = data.get('docs', [])
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
        url = f"https://openlibrary.org/works/{openlibrary_id}.json"
        response = requests.get(url)
        book_detail = {}

        if response.status_code == 200:
            book_data = response.json()
            # You would extract the details you need from book_data and prepare them for your template
            book_detail = {
                'title': book_data.get('title'),
                'authors': [author['name'] for author in book_data.get('authors', [])],
                'publish_date': book_data.get('publish_date'),
                'subjects': [subject['name'] for subject in book_data.get('subjects', [])],
                'cover_id': book_data.get('covers', [])[0] if book_data.get('covers') else None,
                # Add any other details you find useful            }
            }
        return render(request, self.template_name, {'book': book_detail})