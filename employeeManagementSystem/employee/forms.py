from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Employee, Task

class EmployeeCreationForm(UserCreationForm):
    class Meta:
        model = Employee
        fields = [
            'full_name',
            'email',
            'gender',        # dropdown
            'position',      # dropdown
            'date_of_birth',
            'employment_date',
            'phone_number',
            'address',
            'employee_id',
            'department',
            'password1',
            'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "w-full px-3 py-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 mb-3"
            })
class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['assigned_to','title', 'description', 'deadline', 'complete' ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "w-full px-3 py-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 mb-3"
            })