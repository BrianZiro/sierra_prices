from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - Ksh {self.price}"


class EmployeeProfile(models.Model):
    """Extra info for employees created by staff."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_employees',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} (added by {self.added_by.email if self.added_by else '—'})"