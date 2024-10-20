from django.db import models
from passlib.hash import pbkdf2_sha256
import datetime
from user.models import *

class Expense(models.Model):
    """Model representing an expense"""
    SPLIT_METHODS = [
        ('EQUAL', 'Equal'),
        ('EXACT', 'Exact'),
        ('PERCENTAGE', 'Percentage')
    ]
    
    expense_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    split_method = models.CharField(max_length=10, choices=SPLIT_METHODS)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_user = models.CharField(max_length=255)

    def __str__(self):
        return self.description + " " + str(self.expense_id)

    class Meta:
        indexes = [
            models.Index(fields=['created_by']),  # Add index on created_by field
        ]


class Participant(models.Model):
    """Model representing a participant in an expense"""
    participant_id = models.AutoField(primary_key=True)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    split_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['expense', 'user'], name='unique_participant_per_expense')
        ]

    def __str__(self):
        return f"{self.user.name} - {self.expense.expense_id} - {self.expense.description}"
