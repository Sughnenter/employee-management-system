from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Employee, Task, LeaveRequest
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import EmployeeCreationForm


# Create your views here.
class EmployeeLoginView(LoginView):
    template_name = 'employee/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')


def EmployeeLogoutView(request):
        logout(request)
        return redirect('login')


class RegisterEmployeeView(FormView):
    template_name = 'employee/register.html'
    form_class = EmployeeCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterEmployeeView, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user .is_authenticated:
            return redirect ('dashboard')
        return super(RegisterEmployeeView, self).get(*args, **kwargs)

class DashboardView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'employee/dashboard.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        # Only show tasks assigned to the logged-in employee
        return Task.objects.filter(employee=self.request.user).order_by('-deadline')

@require_POST
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, employee=request.user)
    # Task model uses a boolean `complete` field, not a `status` string.
    task.complete = True
    task.save()
    return JsonResponse({'success': True})

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    # include deadline so users can set it; assigned_date is auto-set by the model
    fields = ['title', 'description', 'deadline', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        # The Task model has an `employee` ForeignKey — set that to the logged-in user
        form.instance.employee = self.request.user
        return super(TaskCreate, self).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'deadline', 'complete']
    success_url = reverse_lazy('tasks')
    def form_valid(self, form):
        # The Task model has an `employee` ForeignKey — set that to the logged-in user
        form.instance.employee = self.request.user
        return super(TaskUpdate, self).form_valid(form)

class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')