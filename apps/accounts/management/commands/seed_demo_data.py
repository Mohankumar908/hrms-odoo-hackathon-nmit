"""
Seed realistic demo data for DAYFLOW HRMS.
Creates 6 employees, salary structures, attendance, leave requests,
payroll records, projects, tasks, and work updates.

Usage: python manage.py seed_demo_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random

EMPLOYEES = [
    {
        'employee_id': 'EMP001', 'email': 'arjun.sharma@dayflow.com',
        'password': 'Employee@123', 'role': 'employee',
        'first_name': 'Arjun', 'last_name': 'Sharma',
        'gender': 'male', 'phone': '+91 98765 43210',
        'department': 'Engineering', 'designation': 'Software Engineer',
        'employment_type': 'full_time', 'employment_status': 'active',
        'joining_date': date(2023, 3, 15),
        'date_of_birth': date(1995, 7, 22),
        'basic_salary': 65000, 'house': 15000, 'transport': 5000,
        'medical': 3000, 'tax': 9500, 'pf': 7800,
    },
    {
        'employee_id': 'EMP002', 'email': 'priya.nair@dayflow.com',
        'password': 'Employee@123', 'role': 'employee',
        'first_name': 'Priya', 'last_name': 'Nair',
        'gender': 'female', 'phone': '+91 87654 32109',
        'department': 'Product', 'designation': 'Product Manager',
        'employment_type': 'full_time', 'employment_status': 'active',
        'joining_date': date(2022, 8, 1),
        'date_of_birth': date(1993, 2, 14),
        'basic_salary': 85000, 'house': 20000, 'transport': 6000,
        'medical': 4000, 'tax': 14000, 'pf': 10200,
    },
    {
        'employee_id': 'EMP003', 'email': 'rahul.verma@dayflow.com',
        'password': 'Employee@123', 'role': 'employee',
        'first_name': 'Rahul', 'last_name': 'Verma',
        'gender': 'male', 'phone': '+91 76543 21098',
        'department': 'Engineering', 'designation': 'Senior Software Engineer',
        'employment_type': 'full_time', 'employment_status': 'active',
        'joining_date': date(2021, 11, 20),
        'date_of_birth': date(1990, 11, 30),
        'basic_salary': 95000, 'house': 25000, 'transport': 7000,
        'medical': 5000, 'tax': 18000, 'pf': 11400,
    },
    {
        'employee_id': 'EMP004', 'email': 'sneha.patel@dayflow.com',
        'password': 'Employee@123', 'role': 'employee',
        'first_name': 'Sneha', 'last_name': 'Patel',
        'gender': 'female', 'phone': '+91 65432 10987',
        'department': 'Marketing', 'designation': 'Marketing Manager',
        'employment_type': 'full_time', 'employment_status': 'active',
        'joining_date': date(2023, 6, 5),
        'date_of_birth': date(1994, 5, 18),
        'basic_salary': 72000, 'house': 18000, 'transport': 5500,
        'medical': 3500, 'tax': 11000, 'pf': 8640,
    },
    {
        'employee_id': 'EMP005', 'email': 'karan.mehta@dayflow.com',
        'password': 'Employee@123', 'role': 'employee',
        'first_name': 'Karan', 'last_name': 'Mehta',
        'gender': 'male', 'phone': '+91 54321 09876',
        'department': 'Finance', 'designation': 'Financial Analyst',
        'employment_type': 'full_time', 'employment_status': 'active',
        'joining_date': date(2022, 1, 10),
        'date_of_birth': date(1992, 9, 5),
        'basic_salary': 78000, 'house': 19000, 'transport': 6000,
        'medical': 4000, 'tax': 12500, 'pf': 9360,
    },
    {
        'employee_id': 'EMP006', 'email': 'anjali.reddy@dayflow.com',
        'password': 'Employee@123', 'role': 'employee',
        'first_name': 'Anjali', 'last_name': 'Reddy',
        'gender': 'female', 'phone': '+91 43210 98765',
        'department': 'Customer Support', 'designation': 'Customer Success Manager',
        'employment_type': 'full_time', 'employment_status': 'active',
        'joining_date': date(2023, 9, 1),
        'date_of_birth': date(1996, 3, 27),
        'basic_salary': 58000, 'house': 12000, 'transport': 4000,
        'medical': 2500, 'tax': 7500, 'pf': 6960,
    },
]

PROJECTS = [
    {
        'name': 'HRMS Mobile App',
        'description': 'Building a mobile companion app for DAYFLOW HRMS with attendance, leave, and task tracking.',
        'client': 'Internal',
        'status': 'active',
        'start': date(2026, 1, 15),
        'end': date(2026, 9, 30),
        'manager_id': 'EMP003',
    },
    {
        'name': 'E-Commerce Platform Redesign',
        'description': 'Complete redesign of the client e-commerce platform using React and Django REST.',
        'client': 'RetailMax Pvt Ltd',
        'status': 'active',
        'start': date(2026, 3, 1),
        'end': date(2026, 11, 30),
        'manager_id': 'EMP002',
    },
    {
        'name': 'Payroll Automation System',
        'description': 'Automating the end-to-end payroll processing with bank integration.',
        'client': 'Internal',
        'status': 'planning',
        'start': date(2026, 7, 1),
        'end': date(2026, 12, 31),
        'manager_id': 'EMP002',
    },
]


class Command(BaseCommand):
    help = 'Seeds realistic demo data: employees, salary, attendance, leave, payroll, projects, tasks, work updates.'

    def handle(self, *args, **kwargs):
        from apps.accounts.models import User
        from apps.employees.models import EmployeeProfile, SalaryStructure, Department, Designation
        from apps.leave_management.models import LeaveType, LeaveRequest, LeaveBalance
        from apps.attendance.models import Attendance
        from apps.payroll.models import Payroll
        from apps.projects.models import Project, ProjectMember
        from apps.tasks.models import Task
        from apps.work_updates.models import DailyWorkUpdate
        import calendar

        today = timezone.localdate()
        created_profiles = {}

        # ── 1. Create employees ───────────────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n── Creating employees ──'))
        for d in EMPLOYEES:
            if User.objects.filter(email=d['email']).exists():
                self.stdout.write(f"  Skip (exists): {d['email']}")
                profile = EmployeeProfile.objects.get(user__email=d['email'])
                created_profiles[d['employee_id']] = profile
                continue

            dept = Department.objects.filter(name=d['department']).first()
            desig = Designation.objects.filter(title=d['designation']).first()

            user = User.objects.create_user(
                email=d['email'],
                employee_id=d['employee_id'],
                password=d['password'],
                role=d['role'],
                is_email_verified=True,
            )
            profile = EmployeeProfile.objects.create(
                user=user,
                first_name=d['first_name'],
                last_name=d['last_name'],
                full_name=f"{d['first_name']} {d['last_name']}",
                gender=d['gender'],
                phone=d['phone'],
                department=dept,
                designation=desig,
                joining_date=d['joining_date'],
                date_of_birth=d['date_of_birth'],
                employment_type=d['employment_type'],
                employment_status=d['employment_status'],
            )
            created_profiles[d['employee_id']] = profile
            self.stdout.write(self.style.SUCCESS(f'  Created: {profile.full_name}'))

        # ── 2. Salary structures ──────────────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n── Setting up salary structures ──'))
        for d in EMPLOYEES:
            profile = created_profiles[d['employee_id']]
            sal, new = SalaryStructure.objects.update_or_create(
                employee=profile,
                defaults={
                    'basic_salary': d['basic_salary'],
                    'house_allowance': d['house'],
                    'transport_allowance': d['transport'],
                    'medical_allowance': d['medical'],
                    'other_allowances': 0,
                    'tax_deduction': d['tax'],
                    'provident_fund': d['pf'],
                    'other_deductions': 0,
                    'effective_from': d['joining_date'],
                }
            )
            self.stdout.write(self.style.SUCCESS(
                f"  {'Created' if new else 'Updated'}: {profile.full_name} | Net: ₹{sal.net_salary:,.0f}"
            ))

        # ── 3. Leave balances ─────────────────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n── Setting up leave balances ──'))
        leave_types = list(LeaveType.objects.filter(is_active=True))
        for emp_id, profile in created_profiles.items():
            for lt in leave_types:
                LeaveBalance.objects.get_or_create(
                    employee=profile, leave_type=lt, year=today.year,
                    defaults={'allocated_days': lt.max_days_per_year or 0, 'used_days': 0}
                )
        self.stdout.write(self.style.SUCCESS(f'  Leave balances set for {len(created_profiles)} employees'))

        # ── 4. Attendance — last 30 days ──────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n── Generating attendance records ──'))
        att_count = 0
        for emp_id, profile in created_profiles.items():
            for offset in range(30, 0, -1):
                day = today - timedelta(days=offset)
                if day.weekday() >= 5:   # skip weekends
                    continue
                if Attendance.objects.filter(employee=profile, date=day).exists():
                    continue
                # Realistic distribution: 85% present, 8% leave, 4% absent, 3% half_day
                r = random.random()
                if r < 0.85:
                    checkin_hour  = random.randint(8, 10)
                    checkin_min   = random.randint(0, 59)
                    checkout_hour = random.randint(17, 19)
                    checkout_min  = random.randint(0, 59)
                    from datetime import time, datetime
                    ci = time(checkin_hour, checkin_min)
                    co = time(checkout_hour, checkout_min)
                    dt_in  = datetime.combine(day, ci)
                    dt_out = datetime.combine(day, co)
                    hours  = round((dt_out - dt_in).total_seconds() / 3600, 2)
                    is_late = checkin_hour >= 9 and checkin_min > 15
                    Attendance.objects.create(
                        employee=profile, date=day,
                        check_in=ci, check_out=co,
                        status='present', working_hours=hours,
                        is_late=is_late,
                        is_early_checkout=(hours < 8),
                    )
                elif r < 0.93:
                    Attendance.objects.create(employee=profile, date=day, status='leave')
                elif r < 0.97:
                    Attendance.objects.create(employee=profile, date=day, status='absent')
                else:
                    Attendance.objects.create(
                        employee=profile, date=day, status='half_day',
                        check_in=time(9, 0), check_out=time(13, 0), working_hours=4.0,
                    )
                att_count += 1
        self.stdout.write(self.style.SUCCESS(f'  Created {att_count} attendance records'))

        # ── 5. Leave requests ─────────────────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n── Creating leave requests ──'))
        sick = LeaveType.objects.filter(name='Sick Leave').first()
        casual = LeaveType.objects.filter(name='Casual Leave').first()
        earned = LeaveType.objects.filter(name='Earned Leave').first()

        leave_data = [
            ('EMP001', sick,   today - timedelta(days=12), today - timedelta(days=11), 'approved', 'Fever and cold'),
            ('EMP002', earned, today - timedelta(days=5),  today - timedelta(days=3),  'approved', 'Family function'),
            ('EMP003', casual, today + timedelta(days=3),  today + timedelta(days=4),  'pending',  'Personal work'),
            ('EMP004', sick,   today + timedelta(days=7),  today + timedelta(days=7),  'pending',  'Medical appointment'),
            ('EMP005', earned, today + timedelta(days=15), today + timedelta(days=19), 'pending',  'Vacation'),
            ('EMP006', casual, today - timedelta(days=20), today - timedelta(days=20), 'rejected', 'Personal errand'),
        ]

        admin_user = User.objects.filter(role='admin').first()
        for emp_id, lt, sd, ed, status, reason in leave_data:
            if not lt:
                continue
            profile = created_profiles.get(emp_id)
            if not profile:
                continue
            if LeaveRequest.objects.filter(employee=profile, start_date=sd).exists():
                continue
            lr = LeaveRequest(
                employee=profile, leave_type=lt,
                start_date=sd, end_date=ed, reason=reason, status=status,
            )
            if status in ('approved', 'rejected'):
                lr.reviewed_by = admin_user
                lr.reviewer_comment = 'Reviewed.' if status == 'approved' else 'Insufficient balance / not justified.'
                lr.reviewed_at = timezone.now() - timedelta(days=1)
            lr.save()
            self.stdout.write(self.style.SUCCESS(
                f'  {profile.full_name}: {lt.name} ({sd}→{ed}) [{status}]'
            ))

        # ── 6. Payroll — current month ────────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n── Generating payroll records ──'))
        from apps.payroll import services as payroll_svc
        import calendar as cal_mod
        month, year = today.month, today.year
        for emp_id, profile in created_profiles.items():
            if Payroll.objects.filter(employee=profile, month=month, year=year).exists():
                self.stdout.write(f'  Skip (exists): {profile.full_name}')
                continue
            payroll, err = payroll_svc.generate_payroll(profile.pk, month, year, admin_user)
            if err:
                self.stdout.write(self.style.WARNING(f'  {profile.full_name}: {err}'))
            else:
                payroll.status = 'processed'
                payroll.save(update_fields=['status'])
                self.stdout.write(self.style.SUCCESS(
                    f'  {profile.full_name}: ₹{payroll.net_salary:,.0f} net | {payroll.present_days}d present'
                ))

        # ── 7. Projects ───────────────────────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n── Creating projects ──'))
        all_profiles = list(created_profiles.values())
        proj_objs = {}
        for pd in PROJECTS:
            if Project.objects.filter(name=pd['name']).exists():
                self.stdout.write(f'  Skip (exists): {pd["name"]}')
                proj_objs[pd['name']] = Project.objects.get(name=pd['name'])
                continue
            manager = EmployeeProfile.objects.filter(user__employee_id=pd['manager_id']).first()
            manager_user = manager.user if manager else admin_user
            proj = Project.objects.create(
                name=pd['name'],
                description=pd['description'],
                client=pd['client'],
                status=pd['status'],
                start_date=pd['start'],
                end_date=pd['end'],
                project_manager=manager_user,
            )
            # Add 3-4 team members per project
            members = random.sample(all_profiles, min(4, len(all_profiles)))
            for m in members:
                ProjectMember.objects.get_or_create(project=proj, user=m.user, defaults={'role': 'developer'})
            proj_objs[pd['name']] = proj
            self.stdout.write(self.style.SUCCESS(f'  Created: {proj.name} ({proj.status})'))

        # ── 8. Tasks ──────────────────────────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n── Creating tasks ──'))
        task_templates = [
            ('Design UI wireframes', 'completed', 'high',     100, 10),
            ('Backend API development', 'in_progress', 'high',   65, 20),
            ('Database schema design', 'completed', 'critical',  100, 8),
            ('Unit test coverage', 'in_progress', 'medium',      40, 15),
            ('Code review & QA',  'not_started', 'medium',       0,  12),
            ('Deploy to staging', 'not_started', 'high',         0,   5),
            ('Performance optimization', 'in_progress', 'medium', 30, 16),
            ('Documentation write-up', 'not_started', 'low',      0,  8),
        ]
        task_objs = []
        for proj_name, proj in proj_objs.items():
            members_qs = ProjectMember.objects.filter(project=proj).select_related('user')
            member_users = [m.user for m in members_qs]
            for i, (title, status, priority, progress, est_h) in enumerate(task_templates[:5]):
                full_title = f'{title} — {proj.name[:20]}'
                if Task.objects.filter(title=full_title, project=proj).exists():
                    task_objs.append(Task.objects.get(title=full_title, project=proj))
                    continue
                t = Task.objects.create(
                    title=full_title,
                    description=f'Task for {proj.name}: {title}',
                    project=proj,
                    status=status,
                    priority=priority,
                    progress=progress,
                    estimated_hours=est_h,
                    deadline=proj.end_date - timedelta(days=random.randint(10, 60)) if proj.end_date else None,
                    created_by=admin_user,
                )
                assignees = random.sample(member_users, min(2, len(member_users)))
                t.assignees.set(assignees)
                task_objs.append(t)
            self.stdout.write(self.style.SUCCESS(f'  Tasks created for: {proj.name}'))

        # ── 9. Work updates — last 5 days ────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n── Creating work updates ──'))
        wup_count = 0
        update_samples = [
            ('Completed the API endpoint for user authentication module.',
             'Working on JWT token refresh logic.',
             'Unit tests for auth module.',
             '', 7.5, 70),
            ('Finished UI component library setup with Storybook.',
             'Implementing responsive design for dashboard.',
             'Mobile viewport testing.',
             '', 8.0, 55),
            ('Reviewed and merged 3 pull requests.',
             'Code review for payment module.',
             'Deployment pipeline configuration.',
             'Facing issues with Docker networking on staging.', 7.0, 45),
            ('Completed database migration scripts.',
             'Testing migration on staging environment.',
             'Production deployment approval.',
             '', 6.5, 80),
            ('Wrote unit tests for payroll calculation service.',
             'Integration tests with attendance module.',
             'Test report documentation.',
             '', 8.0, 90),
        ]

        if proj_objs:
            first_proj = list(proj_objs.values())[0]
            tasks_for_proj = Task.objects.filter(project=first_proj)[:3]
            task_list = list(tasks_for_proj)

            for i, (emp_id, profile) in enumerate(list(created_profiles.items())[:5]):
                for day_offset in range(5, 0, -1):
                    work_day = today - timedelta(days=day_offset)
                    if work_day.weekday() >= 5:
                        continue
                    if DailyWorkUpdate.objects.filter(employee=profile, date=work_day, project=first_proj).exists():
                        continue
                    sample = update_samples[i % len(update_samples)]
                    task = task_list[i % len(task_list)] if task_list else None
                    DailyWorkUpdate.objects.create(
                        employee=profile,
                        project=first_proj,
                        task=task,
                        date=work_day,
                        work_completed=sample[0],
                        work_in_progress=sample[1],
                        pending_work=sample[2],
                        blockers=sample[3],
                        hours_worked=sample[4],
                        progress_percentage=sample[5],
                        remarks='On track.' if not sample[3] else 'Need help resolving blocker.',
                    )
                    wup_count += 1

        self.stdout.write(self.style.SUCCESS(f'  Created {wup_count} work updates'))

        # ── Summary ───────────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS('\n' + '═' * 50))
        self.stdout.write(self.style.SUCCESS('✓ Demo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('═' * 50))
        self.stdout.write(f'  Employees  : {EmployeeProfile.objects.filter(user__role="employee").count()}')
        self.stdout.write(f'  Attendance : {Attendance.objects.count()} records')
        self.stdout.write(f'  Leave req  : {LeaveRequest.objects.count()} requests')
        self.stdout.write(f'  Payrolls   : {Payroll.objects.count()} records')
        self.stdout.write(f'  Projects   : {Project.objects.count()}')
        self.stdout.write(f'  Tasks      : {Task.objects.count()}')
        self.stdout.write(f'  Updates    : {DailyWorkUpdate.objects.count()}')
        self.stdout.write('\n  Employee login password: Employee@123')


from apps.projects.models import Project, ProjectMember
