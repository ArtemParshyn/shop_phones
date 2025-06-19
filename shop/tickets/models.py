from django.db import models

from back.models import User

# Create your models here.
class Ticket(models.Model):
    subject = models.CharField(max_length=64, blank=False, null=False)
    description = models.CharField(max_length=128, blank=False, null=False)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'pending'),
        ('resolved', 'resolved'),
        ('closed', 'closed'),
        ('open', 'open')

    ])
    priority = models.CharField(max_length=20, blank=False, choices=[
        ('high', 'high'),
        ('medium', 'medium'),
        ('low', 'low')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, auto_created=True, on_delete=models.CASCADE, related_name='tickets')
