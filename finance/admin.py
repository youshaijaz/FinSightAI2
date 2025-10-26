from django.contrib import admin
from .models import UploadedFile, Loan

admin.site.register(UploadedFile)
admin.site.register(Loan)