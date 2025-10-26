from django.db import models
from django.contrib.auth.models import User

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - ${self.target_amount}"

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


from django.db import models
from django.contrib.auth.models import User

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Link to user

    def __str__(self):
        return f"File {self.id} uploaded at {self.created_at} by {self.user.username if self.user else 'Unknown'}"