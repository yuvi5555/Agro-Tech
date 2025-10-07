from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'message')  # show fields in admin list
    search_fields = ('name', 'email', 'phone')  # add search bar
