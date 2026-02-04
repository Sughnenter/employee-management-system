from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from datetime import date
from decimal import Decimal
from django.core.exceptions import ValidationError

# Create your models here.
class Employee(AbstractUser):
    GENDER_CHOICES=(
        ('male', 'MALE'),
        ('female', 'FEMALE'),
        )
    POSITION_CHOICES=(
        ('manager', 'MANAGER'),
        ('developer', 'DEVELOPER'),
        ('designer', 'DESIGNER'),
        ('tester', 'TESTER'),
        ('hr manager', 'HR MANAGER'),
        ('intern', 'INTERN'),
        ('software engineer', 'SOFTWARE ENGINEER'),
        ('data scientist', 'DATA SCIENTIST'),
        ('product manager', 'PRODUCT MANAGER'),
        ('business analyst', 'BUSINESS ANALYST'),
        ('devops engineer', 'DEVOPS ENGINEER'),
        ('system administrator', 'SYSTEM ADMINISTRATOR'),
        ('network engineer', 'NETWORK ENGINEER'),
        ('technical support', 'TECHNICAL SUPPORT'),
        ('it consultant', 'IT CONSULTANT'),
        ('other', 'OTHER'),
    )
    DEPARTMENT_CHOICES=(
        ('sales', 'SALES'),
        ('resarch & development', 'RESEARCH & DEVELOPMENT'),
        ('software development', 'SOFTWARE DEVELOPMENT'),
        ('product research', 'PRODUCT RESEARCH'),
        ('marketing', 'MARKETING'),
        ('human resource', 'HUMAN RESOURCE'),
        ('legal','LEGAL'),
        ('customer service', 'CUSTOMER SERVICE')
    )
    full_name = models.CharField(max_length=200, blank=True)
    username = None
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    position = models.CharField(max_length=200, blank=True, choices=POSITION_CHOICES)
    date_of_birth = models.DateField(null=True)
    employment_date = models.DateField(default=date.today)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=200, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.CharField(max_length=100, blank=True, choices=DEPARTMENT_CHOICES)

    # Salary stored as a decimal amount in Nigerian Naira. Default assigned to all
    # employees and not exposed on public forms. Use Decimal for money precision.
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('100000.00'))
    # Currency code for clarity; keep non-editable since app uses NGN only
    salary_currency = models.CharField(max_length=3, default='NGN', editable=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

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

MAX_ACTIVE_TASKS = 5
class Task(models.Model):
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="assigned_tasks")
    title = models.CharField(max_length=100) #title of task field
    description = models.TextField() #description of task field
    assigned_date = models.DateField(auto_now_add=True) #date field for assigned date
    deadline = models.DateField() #date field for deadline
    complete = models.BooleanField(default=False)
    
    class Meta():
        ordering = ['complete']

    def __str__(self):
        return f"{self.title} ({self.assigned_to.full_name})"
    def clean(self):
        if not self.complete:
            active_tasks = Task.objects.filter(
                assigned_to=self.assigned_to,
                complete=False
            ).exclude(pk=self.pk).count()

            if active_tasks >= MAX_ACTIVE_TASKS:
                raise ValidationError(
                    f"This employee already has {MAX_ACTIVE_TASKS} active tasks."
                )
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ] # status choices for the leave request
    LEAVE_TYPE=(
        ('sick', 'SICK'),
        ('annual', 'ANNUAL'),
        ('unpaid', 'UNPAID'),
        ('maternity', 'MATERNITY'),
        ('paternity', 'PATERNITY'),
        ('bereavement', 'BEREAVEMENT'),
        ('other', 'OTHER'),
        )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField() #date field for start date
    end_date = models.DateField() #date field for end date
    reason = models.TextField() #reason for leave field
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE, default='other') #leave type field with choices
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending') #status field with choices
    applied_on = models.DateField(auto_now_add=True) #date field for applied on
    # `updated_at` should reflect the last modification (e.g., when status is changed).
    # Use auto_now so it updates on every save.
    updated_at = models.DateTimeField(auto_now=True)

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
