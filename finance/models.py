from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Loan(models.Model):
    client_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, default='Active')  # e.g., Active, Paid, Overdue


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"File {self.id} uploaded at {self.created_at}"