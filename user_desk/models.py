from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
    ('admin', 'ADMIN'),
    ('user', 'USER'),
    ('agent', 'AGENT'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
class Ticket(models.Model):
    PRIORITY_CHOICES = (
    ('low', 'LOW'),
    ('medium', 'MEDIUM'),
    ('high', 'HIGH'),
    )
    STATUS_CHOICES = (
    ('open', 'OPEN'),
    ('in-progress', 'IN PROGRESS'),
    ('resolved', 'RESOLVED'),
    ('closed', 'CLOSED'),
    ('escalated', 'ESCALATED'),
    )
    title = models.CharField(max_length=50)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="open")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tickets_created')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets")
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(auto_now=True)

