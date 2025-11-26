from django.urls import path
from . import views
from .views import EmployeeLoginView, EmployeeLogoutView, RegisterEmployeeView, DashboardView, TaskCreate, LeaveRequestCreateView, ApproveLeaveRequestView, update_leave_status, CompleteTaskView,

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path ('login/', EmployeeLoginView.as_view(), name='login' ),
    path('logout/', EmployeeLogoutView, name='logout'),
    path('register/', RegisterEmployeeView.as_view(), name='register'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('task-create/', views.TaskCreate.as_view(), name='create_task'),
    path('leave-request/', views.LeaveRequestCreateView.as_view(), name='leave_request'),
    path('leave-approval/', views.ApproveLeaveRequestView.as_view(), name='leave_approve'),
    path("leave/<int:pk>/<str:action>/", update_leave_status, name="update-leave"),
    path('task/<int:task_id>/complete/', CompleteTaskView.as_view(), name='complete_task'),

]
