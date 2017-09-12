from django.contrib import admin
from .models import Investor, Document

class InvestorAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_date')

admin.site.register(Investor, InvestorAdmin)
admin.site.register(Document)
