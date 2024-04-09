# books/urls.py
from django.urls import path
from .views import BookListView, AuthorListView, BookDetailView, HomePageView, SignUpView, user_dashboard, add_to_shelf, BookUpdateView, BookDeleteView
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [

    #book views
    path('', HomePageView.as_view(), name='home'),
    path('books/', BookListView.as_view(), name='book-list'),
    path('authors/', AuthorListView.as_view(), name='author-list'),
    path('books/<str:openlibrary_id>/', BookDetailView.as_view(), name='book-detail'),
    path('add-to-shelf/<str:openlibrary_id>/', add_to_shelf, name='add-to-shelf'),
    path('books/edit/<int:pk>/', BookUpdateView.as_view(), name='edit-book'),
    path('books/<int:pk>/confirm_delete/', BookDeleteView.as_view(), name='book-confirm-delete'),


    #registration
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='books/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    #user dashboard
    path('dashboard/', user_dashboard, name='user-dashboard'),

]
