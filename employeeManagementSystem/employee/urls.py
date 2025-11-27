from django.urls import path
from . import views
from .views import EmployeeLoginView, EmployeeLogoutView, RegisterEmployeeView, DashboardView, TaskCreate, LeaveRequestCreateView, ApproveLeaveRequestView, update_leave_status, CompleteTaskView, EmployeeDetailView, EmployeeListView, export_employees_csv, DeleteEmployeeView, UpdateEmployeeView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path ('login/', EmployeeLoginView.as_view(), name='login' ),
    path('logout/', EmployeeLogoutView, name='logout'),
    path('register/', RegisterEmployeeView.as_view(), name='register'),
    path('task/<int:task_id>/complete/', CompleteTaskView.as_view(), name='complete_task'),
    path('task-create/', TaskCreate.as_view(), name='create_task'),
    path('leave-request/', LeaveRequestCreateView.as_view(), name='leave_request'),
    path('leave-approval/', ApproveLeaveRequestView.as_view(), name='leave_approve'),
    path("leave/<int:pk>/<str:action>/", update_leave_status, name="update-leave"),
    path('employee/<int:pk>/', EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/', EmployeeListView.as_view(), name='employee_list'),
    path('export-employees/', views.export_employees_csv, name='export_employees_csv'),
    path('employee/<int:pk>/delete/', DeleteEmployeeView.as_view(), name='delete_employee'),
    path('employee/<int:pk>/update/', UpdateEmployeeView.as_view(), name='update_employee'),

]
