from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .forms import UserAdminChangeForm, UserAdminCreationForm
from .models import (
    College,
    Degree,
    Department,
    InstructorProfile,
    PlanType,
    Profile,
    Registration,
    StudentProfile,
    Subscription,
    SubscriptionHistory,
    User,
)


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        "id",
        "email",
        "full_name",
        "is_active",
        "is_admin",
        "is_staff",
        "date_joined",
        "last_login",
    )
    list_filter = (
        "is_admin",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        ("Personal info", {"fields": ("full_name",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_admin",
                    "is_staff",
                    "is_active",
                )
            },
        ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = (
        "email",
        "full_name",
    )
    ordering = ("email",)
    filter_horizontal = ()


class PlanTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    search_fields = ("name",)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "plan_type",
        "no_of_courses",
        "no_of_students_per_course",
        "prog_assign_enabled",
        "subjective_assign_enabled",
        "email_enabled",
        "per_video_limit",
        "per_video_limit_unit",
        "total_video_limit",
        "total_video_limit_unit",
        "subjective_assign_submission_size_per_student",
        "subjective_assign_submission_size_per_student_unit",
    )
    search_fields = ("plan_type__name",)


class SubscriptionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "subscription",
        "start_date",
        "duration",
        "purchased_on",
        "modified_on",
    )
    search_fields = ("user__email",)


class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "activation_key",
        "forgot_password",
        "created_on",
    )
    search_fields = ("user__email",)


class CollegeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class DegreeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "gender",
        "college",
        "city",
        "state",
        "created_on",
        "modified_on",
    )
    search_fields = (
        "user__email",
        "gender",
        "college",
        "city",
        "state",
        "created_on",
        "modified_on",
    )


class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "domain",
    )
    search_fields = ("profile", "domain", "college")


class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "roll_no",
        "department",
        "degree",
        "year_of_passing",
    )
    search_fields = ("profile", "roll_no", "department", "degree", "year_of_passing")


admin.site.register(User, UserAdmin)
# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)
admin.site.register(PlanType, PlanTypeAdmin)
admin.site.register(SubscriptionHistory, SubscriptionHistoryAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(College, CollegeAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Degree, DegreeAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(InstructorProfile, InstructorProfileAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
