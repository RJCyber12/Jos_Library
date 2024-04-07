# Generated by Django 5.0.3 on 2024-04-07 02:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='summary',
        ),
        migrations.AddField(
            model_name='book',
            name='openlibrary_id',
            field=models.CharField(default='OL3173874W', max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Shelf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='My Shelf', max_length=255)),
                ('books', models.ManyToManyField(related_name='shelves', to='books.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shelves', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
