from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.conf import settings


class UserManager(BaseUserManager):

    def create_user(self,
                    email,
                    password=None,
                    full_name='',
                    is_active=None,
                    is_staff=None,
                    is_admin=False):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email),)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password=None):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    full_name = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)  # a superuser
    # notice the absence of a "Password field", that is built in.
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
    ]  # Email & Password are required by default in createsuperuser command.

    objects = UserManager()

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active


class PlanType(models.Model):
    name = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)

    def __str__(self):
        return self.name


UNIT = (
    ('KB', 'Kilobytes'),
    ('MB', 'MegaBytes'),
    ('GB', 'GigaBytes'),
    ('TB', 'TeraBytes'),
)


class Subscription(models.Model):
    plan_type = models.ForeignKey(PlanType, on_delete=models.CASCADE)
    no_of_courses = models.IntegerField()
    no_of_students_per_course = models.IntegerField()

    prog_assign_enabled = models.BooleanField()
    subjective_lab_enabled = models.BooleanField()
    email_enabled = models.BooleanField()

    per_video_limit = models.FloatField()
    per_video_limit_unit = models.CharField(max_length=2, choices=UNIT)

    total_video_limit = models.FloatField()
    total_video_limit_unit = models.CharField(max_length=2, choices=UNIT)

    subjective_lab_submission_size_per_student = models.FloatField()
    subjective_lab_submission_size_per_student_unit = models.CharField(
        max_length=2, choices=UNIT)

    def __str__(self):
        return self.plan_type.name


class SubscriptionHistory(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField()
    purchased_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s : %s" % (str(
            self.user.email), self.subscription.plan_type.name)
