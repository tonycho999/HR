from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    TEAM_CHOICES = (
        ('IT', 'IT Team'),
        ('HR', 'HR Team'),
        ('SALES', 'Sales Team'),
        ('SUPPORT', 'Support Team'),
    )
    team = models.CharField(max_length=50, choices=TEAM_CHOICES, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    last_ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return self.username

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time_in = models.DateTimeField(auto_now_add=True)
    time_out = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

class Leave(models.Model):
    LEAVE_TYPES = (
        ('VL', 'Vacation Leave'),
        ('SL', 'Sick Leave'),
        ('EL', 'Emergency Leave'),
        ('HL', 'Holiday Leave'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=2, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.status})"

class Payroll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2)
    is_approved = models.BooleanField(default=False)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    target_team = models.CharField(max_length=50, choices=User.TEAM_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
