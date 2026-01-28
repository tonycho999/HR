from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from .models import User, Attendance, Leave, Payroll, Announcement
from .forms import LeaveForm
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
import os

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class CustomLoginView(LoginView):
    template_name = 'core/login.html'

    def form_valid(self, form):
        # Update user's last IP
        user = form.get_user()
        user.last_ip_address = get_client_ip(self.request)
        user.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    return render(request, 'core/profile.html')

@login_required
def dashboard(request):
    # Determine user's latest attendance status
    # Look for an active session (not timed out)
    attendance = Attendance.objects.filter(user=request.user, time_out__isnull=True).order_by('-time_in').first()

    # Announcements
    # Show announcements for everyone (target_team is None) or user's team
    announcements = Announcement.objects.filter(
        Q(target_team__isnull=True) | Q(target_team=request.user.team)
    ).order_by('-created_at')[:5]

    context = {
        'attendance': attendance,
        'announcements': announcements,
        'user_ip': get_client_ip(request)
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def time_in(request):
    if request.method == 'POST':
        # Check if already timed in (active session exists)
        existing = Attendance.objects.filter(user=request.user, time_out__isnull=True).exists()
        if not existing:
            Attendance.objects.create(
                user=request.user,
                ip_address=get_client_ip(request)
            )
    return redirect('dashboard')

@login_required
def time_out(request):
    if request.method == 'POST':
        # Find active session
        attendance = Attendance.objects.filter(user=request.user, time_out__isnull=True).order_by('-time_in').first()
        if attendance:
            attendance.time_out = timezone.now()
            attendance.save()
    return redirect('dashboard')

@login_required
def leave_request(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user
            leave.save()
            return redirect('leave_list')
    else:
        form = LeaveForm()
    return render(request, 'core/leave_request.html', {'form': form})

@login_required
def leave_list(request):
    leave_list = Leave.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(leave_list, 10)  # Show 10 leaves per page
    page_number = request.GET.get('page')
    leaves = paginator.get_page(page_number)
    return render(request, 'core/leave_list.html', {'leaves': leaves})

@login_required
def leave_approval_list(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    leaves = Leave.objects.filter(status='PENDING').order_by('created_at')
    return render(request, 'core/leave_approval.html', {'leaves': leaves})

@login_required
def approve_leave(request, leave_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    leave = get_object_or_404(Leave, id=leave_id)
    leave.status = 'APPROVED'
    leave.save()
    return redirect('leave_approval')

@login_required
def reject_leave(request, leave_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    leave = get_object_or_404(Leave, id=leave_id)
    leave.status = 'REJECTED'
    leave.save()
    return redirect('leave_approval')

@login_required
def payroll_list(request):
    payroll_list = Payroll.objects.filter(user=request.user, is_approved=True).order_by('-year', '-month')
    paginator = Paginator(payroll_list, 10)  # Show 10 payrolls per page
    page_number = request.GET.get('page')
    payrolls = paginator.get_page(page_number)
    return render(request, 'core/payroll_list.html', {'payrolls': payrolls})

@login_required
def payroll_detail(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk, user=request.user)
    return render(request, 'core/payroll_detail.html', {'payroll': payroll})

@login_required
def announcement_list(request):
    announcements = Announcement.objects.filter(
        Q(target_team__isnull=True) | Q(target_team=request.user.team)
    ).order_by('-created_at')
    return render(request, 'core/announcement_list.html', {'announcements': announcements})

@login_required
def payroll_approval_list(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    payrolls = Payroll.objects.filter(is_approved=False).order_by('year', 'month')
    return render(request, 'core/payroll_approval.html', {'payrolls': payrolls})

@login_required
def approve_payroll(request, payroll_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    payroll = get_object_or_404(Payroll, id=payroll_id)
    payroll.is_approved = True
    payroll.save()
    return redirect('payroll_approval')

def manifest(request):
    return HttpResponse(
        open(os.path.join(settings.BASE_DIR, 'core/static/core/manifest.json')).read(),
        content_type='application/json'
    )

def service_worker(request):
    return HttpResponse(
        open(os.path.join(settings.BASE_DIR, 'core/static/core/sw.js')).read(),
        content_type='application/javascript'
    )
