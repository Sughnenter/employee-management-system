from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from datetime import date

# Create your models here.
class Employee(AbstractUser):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        # Only generate employee_id if it doesn’t exist
        if not self.employee_id:
            with transaction.atomic():
                last_emp = Employee.objects.select_for_update().order_by('-id').first()
                if last_emp and last_emp.employee_id and last_emp.employee_id.startswith('EMP'):
                    try:
                        num = int(last_emp.employee_id.replace('EMP', '')) + 1
                    except ValueError:
                        num = last_emp.id + 1
                else:
                    num = 1
                self.employee_id = f"EMP{num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

# Creates a model for employees extending the default Django User model with additional fields.

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=date.today, db_index=True)
    check_in = models.TimeField(null=True, blank=True) #time field for check in
    check_out = models.TimeField(null=True, blank=True) #time field for check out
    status = models.CharField(
        max_length=10,
        choices=[('Present', 'Present'), ('Absent', 'Absent'), ('On Leave', 'On Leave')],
        default='Present'
    )
    remarks = models.TextField(blank=True, null=True)  # for custom notes like "Medical leave" or "Arrived 1hr late"

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        # Use the employee's __str__ to avoid relying on username attribute
        return f"{self.employee} - {self.date} ({self.status})"

class Task(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100) #title of task field
    description = models.TextField() #description of task field
    assigned_date = models.DateField(auto_now_add=True) #date field for assigned date
    deadline = models.DateField() #date field for deadline
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Completed', 'Completed')],
        default='Pending'
    )

    class Meta:
        ordering = ['status', 'deadline']


    def __str__(self):
        return f"{self.title} ({self.employee})"

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ] # status choices for the leave request

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField() #date field for start date
    end_date = models.DateField() #date field for end date
    reason = models.TextField() #reason for leave field
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending') #status field with choices
    applied_on = models.DateField(auto_now_add=True) #date field for applied on

    class Meta:
        ordering = ['-applied_on']
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"

    @property
    def is_active_today(self):
        today = date.today()
        return self.status == 'Approved' and self.start_date <= today <= self.end_date


    def __str__(self):
        return f"{self.employee} - {self.status}"