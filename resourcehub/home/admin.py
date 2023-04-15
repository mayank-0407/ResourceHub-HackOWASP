from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Customer)
admin.site.register(plan)
admin.site.register(userType)
admin.site.register(Draft)
admin.site.register(review)