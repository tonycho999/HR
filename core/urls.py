from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('time_in/', views.time_in, name='time_in'),
    path('time_out/', views.time_out, name='time_out'),
    path('leave/request/', views.leave_request, name='leave_request'),
    path('leave/list/', views.leave_list, name='leave_list'),
    path('leave/approval/', views.leave_approval_list, name='leave_approval'),
    path('leave/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('leave/reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/<int:pk>/', views.payroll_detail, name='payroll_detail'),
    path('payroll/approval/', views.payroll_approval_list, name='payroll_approval'),
    path('payroll/approve/<int:payroll_id>/', views.approve_payroll, name='approve_payroll'),
    path('announcements/', views.announcement_list, name='announcement_list'),
]
