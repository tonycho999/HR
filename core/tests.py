from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Attendance, Leave, Payroll, Announcement
from django.utils import timezone
import datetime

class BPOSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password', team='IT')
        self.admin = User.objects.create_superuser(username='admin', password='password', is_staff=True)

    def test_login_and_dashboard(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password'})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_attendance_logic(self):
        self.client.login(username='testuser', password='password')

        # Time In
        response = self.client.post(reverse('time_in'))
        self.assertEqual(response.status_code, 302)

        # Check active session
        attendance = Attendance.objects.filter(user=self.user, time_out__isnull=True).first()
        self.assertIsNotNone(attendance)
        self.assertIsNotNone(attendance.time_in)

        # Time Out
        response = self.client.post(reverse('time_out'))
        attendance.refresh_from_db()
        self.assertIsNotNone(attendance.time_out)

    def test_overnight_attendance(self):
        self.client.login(username='testuser', password='password')

        # Mock Time In yesterday
        yesterday = timezone.now() - datetime.timedelta(days=1)
        att = Attendance.objects.create(user=self.user, time_in=yesterday, date=yesterday.date())

        # Verify creation time
        self.assertTrue((att.time_in - yesterday).total_seconds() < 5)
        self.assertEqual(att.date, yesterday.date())

        # Time Out (should close yesterday's session even if it is today now)
        response = self.client.post(reverse('time_out'))
        attendance = Attendance.objects.get(user=self.user)
        self.assertIsNotNone(attendance.time_out)

    def test_leave_logic(self):
        self.client.login(username='testuser', password='password')
        start_date = timezone.now().date() + datetime.timedelta(days=1)
        end_date = start_date + datetime.timedelta(days=2)

        response = self.client.post(reverse('leave_request'), {
            'leave_type': 'VL',
            'start_date': start_date,
            'end_date': end_date,
            'reason': 'Vacation'
        })
        self.assertEqual(response.status_code, 302)
        leave = Leave.objects.get(user=self.user)
        self.assertEqual(leave.status, 'PENDING')

        # Admin Approve
        self.client.logout()
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('approve_leave', args=[leave.id]))
        leave.refresh_from_db()
        self.assertEqual(leave.status, 'APPROVED')

    def test_payroll_visibility(self):
        Payroll.objects.create(
            user=self.user, month=1, year=2024, base_salary=1000,
            net_pay=900, is_approved=True
        )
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('payroll_list'))
        self.assertContains(response, '900')

    def test_announcement_filtering(self):
        Announcement.objects.create(title="General", content="All", target_team=None)
        Announcement.objects.create(title="IT Only", content="IT stuff", target_team='IT')
        Announcement.objects.create(title="HR Only", content="HR stuff", target_team='HR')

        self.client.login(username='testuser', password='password') # IT team
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, "General")
        self.assertContains(response, "IT Only")
        self.assertNotContains(response, "HR Only")
