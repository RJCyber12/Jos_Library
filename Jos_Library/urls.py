# Jos_Library/urls.py
from django.contrib import admin
from django.urls import path, include
from books.views import HomePageView


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('books/', include('books.urls')),

]
