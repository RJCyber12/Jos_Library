
# books/models.py
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    summary = models.TextField()
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.title
