# Jos_Library/urls.py
from django.contrib import admin
from django.urls import path, include
from books.views import HomePageView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', include('books.urls')),
    path('', HomePageView.as_view(), name='home'),  # Root URL
  # Include the URLs from the books app
    # Remove direct view imports and usage here
]
