from django.contrib import admin

# Register your models here.

from .models import Entry, Comment, Author

admin.site.register(Entry)
admin.site.register(Comment)
admin.site.register(Author)
