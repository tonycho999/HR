from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Attendance, Leave, Payroll, Announcement

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'team', 'position', 'last_ip_address', 'is_staff')
    list_filter = ('team', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('BPO Info', {'fields': ('team', 'position', 'last_ip_address')}),
    )

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'time_in', 'time_out', 'ip_address')
    list_filter = ('date', 'user__team')
    search_fields = ('user__username',)

class LeaveAdmin(admin.ModelAdmin):
    list_display = ('user', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'leave_type', 'user__team')
    actions = ['approve_leaves', 'reject_leaves']

    def approve_leaves(self, request, queryset):
        queryset.update(status='APPROVED')
    approve_leaves.short_description = "Approve selected leaves"

    def reject_leaves(self, request, queryset):
        queryset.update(status='REJECTED')
    reject_leaves.short_description = "Reject selected leaves"

class PayrollAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'year', 'net_pay', 'is_approved')
    list_filter = ('month', 'year', 'is_approved', 'user__team')
    actions = ['approve_payroll']

    def approve_payroll(self, request, queryset):
        queryset.update(is_approved=True)
    approve_payroll.short_description = "Approve selected payrolls"

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_team', 'created_at')
    list_filter = ('target_team',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Leave, LeaveAdmin)
admin.site.register(Payroll, PayrollAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
