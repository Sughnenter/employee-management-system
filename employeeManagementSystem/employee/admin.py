from django.contrib import admin
from .models import Employee, Task, LeaveRequest


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
	list_display = (
		'full_name',
		'email',
		'department',
		'position',
		'employee_id',
		'salary',
		'salary_currency',
	)
	search_fields = ('full_name', 'email', 'employee_id')
	list_filter = ('department', 'position')


admin.site.register(Task)
admin.site.register(LeaveRequest)