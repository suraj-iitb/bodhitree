from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import User, PlanType, Subscription, SubscriptionHistory

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'admin')
    list_filter = ('admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('admin',)}),
        ('Important dates', {'fields': ('last_login', )})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

class PlanTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['plan_type', 'no_of_courses', 'no_of_students_per_course', 
    'prog_assign_enabled', 'subjective_lab_enabled', 'email_enabled', 'per_video_limit',
    'per_video_limit_unit', 'total_video_limit', 'total_video_limit_unit',
    'subjective_lab_submission_size_per_student', 'subjective_lab_submission_size_per_student_unit']
    search_fields = ('plan_type__name',)

class SubscriptionHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription', 'start_date', 'duration']
    search_fields = ['user__email']


admin.site.register(PlanType, PlanTypeAdmin)
admin.site.register(SubscriptionHistory, SubscriptionHistoryAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(User, UserAdmin)
# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)