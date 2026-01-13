from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Employee, Task, LeaveRequest
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import EmployeeCreationForm, LeaveRequestForm, TaskForm
from datetime import date, timedelta
from django.views import View
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Q
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.views.generic import TemplateView
from django.db.models import Count
from django.utils import timezone


# Create your views here.

class AdminOnlyMixin(UserPassesTestMixin):
    model = Employee
    
    def test_func(self):
        # Only allow superusers
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        # Custom redirect or message
        return redirect('dashboard')
    
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

class DeleteEmployeeView(LoginRequiredMixin, AdminOnlyMixin, DeleteView):
    model = Employee
    template_name = 'employee/employee_delete.html'
    success_url = reverse_lazy('employee_list')

class UpdateEmployeeView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = Employee
    fields = ['full_name', 'position', 'employment_date', 'phone_number', 'address', "department"] 
    template_name = "employee/employee_update.html"
    success_url = reverse_lazy("employee_list")

    

class DashboardView(LoginRequiredMixin, ListView):
    model = Task, LeaveRequest
    template_name = 'employee/dashboard.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        today = timezone.now().date()
        return Task.objects.filter(
            assigned_to=self.request.user,
            complete=False,
            deadline__gte=today
        ).order_by('deadline')
        
    def get_context_data(self, **kwargs):
        today = timezone.now().date()
        grace_period = today - timedelta(days=3)
        expired_rejected_cutoff = timezone.now() - timedelta(days=3)
        ctx = super().get_context_data(**kwargs)
        ctx['leave_requests'] = LeaveRequest.objects.filter(
            employee=self.request.user
        )
        ctx['overdue_tasks'] = Task.objects.filter(
            assigned_to=self.request.user,
            complete=False,
            deadline__lt=today,
            deadline__gte=grace_period
        )
        
        # ctx['active_leaves'] = LeaveRequest.objects.filter(
        #     employee=self.request.user,
        #     status='Approved',
        #     end_date__gte=today
        # )

        # All visible leaves (exclude expired rejected ones)
        ctx['leave_requests'] = LeaveRequest.objects.filter(
            employee=self.request.user
        ).exclude(
            Q(status='Rejected') & Q(updated_at__lt=expired_rejected_cutoff)
        )

        # Recently rejected (for alert banner)
        ctx['recent_rejected_leaves'] = LeaveRequest.objects.filter(
            employee=self.request.user,
            status='Rejected',
            updated_at__gte=expired_rejected_cutoff
        )

        return ctx


class TaskCreate(AdminOnlyMixin, LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'employee/task_create.html'
    fields = ['title', 'description', 'deadline', 'assigned_to']
    success_url = reverse_lazy('dashboard')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['assigned_to'].queryset = Employee.objects.all()
        return form


class CompleteTaskView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)

        # Security check — only the employee assigned can complete the task
        if not (request.user.is_staff or task.assigned_to == request.user):
            return redirect('dashboard')   # or raise PermissionDenied

        task.complete = True
        task.save()

        return redirect('dashboard')

class TaskUpdate(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'deadline', 'complete']
    success_url = reverse_lazy('tasks')
    def form_valid(self, form):
        # The Task model has an `employee` ForeignKey — set that to the logged-in user
        form.instance.employee = self.request.user
        return super(TaskUpdate, self).form_valid(form)

class TaskDelete(LoginRequiredMixin, AdminOnlyMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('dashboard')

class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'employee/leave_request.html'
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['employee'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.employee = self.request.user
        return super().form_valid(form)

class ApproveLeaveRequestView(LoginRequiredMixin, AdminOnlyMixin, ListView):
    model = LeaveRequest
    template_name = 'employee/leave_approval.html'
    context_object_name = 'leave_requests'

def update_leave_status(request, pk, action):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)

    if not (request.user.is_staff or request.user.is_admin):
        return redirect("dashboard")

    if action == "approve":
        leave_request.status = "Approved"
    elif action == "reject":
        leave_request.status = "Rejected"

    leave_request.save()
    return redirect("leave_approve")    

class EmployeeDetailView(AdminOnlyMixin, DetailView):
    model = Employee
    template_name = 'employee/employee_detail.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()

        context['tasks'] = employee.assigned_tasks.all()
        context['completed_tasks'] = employee.assigned_tasks.filter(complete=True).count()
        context['leave_requests'] = employee.leave_requests.all()

        return context

class EmployeeListView(LoginRequiredMixin, AdminOnlyMixin, ListView):
    model = Employee
    template_name = 'employee/employee_list.html'
    context_object_name = 'employees'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")

        if q:
            qs = qs.filter(
                Q(full_name__icontains=q) |
                Q(email__icontains=q) |
                Q(department__icontains=q)
            )
        department = self.request.GET.get("department")
        if department and department != "all":
            qs = qs.filter(department=department)

        return qs
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["departments"] = Employee.objects.values_list("department", flat=True).distinct()
        return ctx


def export_employees_csv(request):
    if not request.user.is_superuser:
        return redirect("dashboard")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="employees.csv"'
    writer = csv.writer(response)
    writer.writerow(["Full Name", "Email", "Gender", "Date of Birth", "Employment date", "Phone number", "Address", "ID" "Department", "Position"])
    for emp in Employee.objects.all():
        writer.writerow([
            emp.full_name,
            emp.email,
            emp.gender,
            emp.date_of_birth,
            emp.employment_date,
            emp.phone_number,
            emp.address,
            emp.employee_id,
            emp.department,
            emp.get_position_display(),  # Get human-readable choice label
        ])

    return response
class ExportEmployeesPDFView(LoginRequiredMixin, AdminOnlyMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="employees.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        y = 750

        employees = Employee.objects.all()

        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 770, "Employee Report")
        p.setFont("Helvetica", 10)

        for emp in employees:
            p.drawString(50, y, f"{emp.full_name} | {emp.email} | {emp.department}")
            y -= 20
            if y < 50:
                p.showPage()
                y = 750

        p.save()
        return response

class AdminAnalyticsView(LoginRequiredMixin, AdminOnlyMixin, TemplateView):
    template_name = "employee/analytics.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["employee_count"] = Employee.objects.count()
        ctx["active_tasks"] = Task.objects.filter(complete=False).count()
        ctx["completed_tasks"] = Task.objects.filter(complete=True).count()
        ctx["pending_leave"] = LeaveRequest.objects.filter(status="Pending").count()
        ctx["approved_leave"] = LeaveRequest.objects.filter(status="Approved").count()

        # For charts later:
        ctx["department_distribution"] = (
            Employee.objects.values("department")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return ctx
