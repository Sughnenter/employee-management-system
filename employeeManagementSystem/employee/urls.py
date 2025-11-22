from django.urls import path
from . import views
from .views import EmployeeLoginView, EmployeeLogoutView, RegisterEmployeeView, DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path ('login/', EmployeeLoginView.as_view(), name='login' ),
    path('logout/', EmployeeLogoutView, name='logout'),
    path('register/', RegisterEmployeeView.as_view(), name='register'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),
]
