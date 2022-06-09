from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ServiceProvider)
admin.site.register(Paypoint)
admin.site.register(ServiceProviderLegalForm)
admin.site.register(ServiceProviderLevel)
admin.site.register(ServiceProviderSubLevel)