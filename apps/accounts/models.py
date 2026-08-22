"""
DAYFLOW HRMS - Custom User model with role-based access.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from core.models import TimeStampedModel
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, employee_id, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not employee_id:
            raise ValueError('Employee ID is required')
        email = self.normalize_email(email)
        user = self.model(email=email, employee_id=employee_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, employee_id, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_email_verified', True)
        return self.create_user(email, employee_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('employee', 'Employee'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    password_reset_token = models.UUIDField(null=True, blank=True)
    password_reset_token_created = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['employee_id']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.employee_id} - {self.email}'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_hr(self):
        return self.role == 'hr'

    @property
    def is_employee(self):
        return self.role == 'employee'

    @property
    def full_name(self):
        if hasattr(self, 'employee_profile'):
            return self.employee_profile.full_name
        return self.email
