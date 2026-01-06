from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Employee, Task, LeaveRequest

class EmployeeCreationForm(UserCreationForm):
    class Meta:
        model = Employee
        fields = [
            'full_name',
            'email',
            'gender',
            'date_of_birth',
            'employment_date',
            'position',
            'department',
            'phone_number',
            'address',
            'employee_id',
            'password1',
            'password2'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'employment_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "w-full px-3 py-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 mb-3"
            })
    def save(self, commit=True):
        user = super().save(commit=False)
        # Set username to email to satisfy the UNIQUE constraint
        user.username = user.email
        if commit:
            user.save()
        return user
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
    widgets = {
            'deadline': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-2 bg-gray-800 text-white border border-gray-600 rounded-lg'
            })
        }        

class LeaveRequestForm(ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['employee', 'start_date', 'end_date', 'reason', 'leave_type', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "w-full px-3 py-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 mb-3"
            })

    widgets = {
            "leave_type": forms.Select(attrs={
                "class": "w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            }),
            "start_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            }),
            "end_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            }),
            "reason": forms.Textarea(attrs={
                "class": "w-full border border-gray-300 rounded-lg p-3 h-32 focus:ring-2 focus:ring-blue-500 focus:outline-none",
                "placeholder": "Explain why you’re applying for leave…"
            }),
        }