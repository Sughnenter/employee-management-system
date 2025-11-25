from django.contrib import admin
from .models import Employee, Task, LeaveRequest

# Register your models here.
admin.site.register(Employee)
admin.site.register(Task) 
admin.site.register(LeaveRequest) 