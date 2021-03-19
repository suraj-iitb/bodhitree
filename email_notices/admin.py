from django.contrib import admin

from email_notices.models import Email

class EmailAdmin(admin.ModelAdmin):
    list_display = ('id','course', 'sender')
    search_fields = ('course__title',)


admin.site.register(Email, EmailAdmin)
