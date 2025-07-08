from django.contrib import admin
from .models import BillDetails, BillDetailItems

# Register your models here.
admin.site.register(BillDetails)
admin.site.register(BillDetailItems)
