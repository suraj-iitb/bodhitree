from django.contrib import admin

from email_notices.models import Email

class EmailAdmin(admin.ModelAdmin):
    list_display = ('id','course', 'sender')

admin.site.register(Email, EmailAdmin)
