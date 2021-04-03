from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


UNIT = (
    ("KB", "KiloBytes"),
    ("MB", "MegaBytes"),
    ("GB", "GigaBytes"),
    ("TB", "TeraBytes"),
)


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password=None,
    ):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

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
        user.is_staff = True
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
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="email address", unique=True)
    full_name = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)  # a superuser
    # notice the absence of a "password" field, that is built in.
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        []
    )  # Email & Password are required by default in createsuperuser command.

    objects = UserManager()

    class Meta:
        ordering = ["-id"]

    def get_full_name(self):
        # The user is identified by their email address
        return self.full_name

    def get_short_name(self):
        # The user is identified by their email address
        return self.full_name

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


class PlanType(models.Model):
    name = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH, unique=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    plan_type = models.OneToOneField(PlanType, on_delete=models.CASCADE)
    no_of_courses = models.IntegerField()
    no_of_students_per_course = models.IntegerField()

    prog_assign_enabled = models.BooleanField()
    subjective_assign_enabled = models.BooleanField()
    email_enabled = models.BooleanField()

    per_video_limit = models.FloatField()
    per_video_limit_unit = models.CharField(max_length=2, choices=UNIT)

    total_video_limit = models.FloatField()
    total_video_limit_unit = models.CharField(max_length=2, choices=UNIT)

    subjective_assign_submission_size_per_student = models.FloatField()
    subjective_assign_submission_size_per_student_unit = models.CharField(
        max_length=2, choices=UNIT
    )

    def __str__(self):
        return self.plan_type.name


class SubscriptionHistory(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField()
    purchased_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.user.email, self.subscription.plan_type.name)
