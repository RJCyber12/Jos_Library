# Generated by Django 5.0.3 on 2024-04-08 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_customuser_is_staff'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='author',
        ),
        migrations.AddField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(related_name='books', to='books.author'),
        ),
    ]