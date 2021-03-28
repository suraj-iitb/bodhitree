from django.contrib import admin

from cribs.models import Crib, CribReply


class CribAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "created_by", "title")


class CribReplyAdmin(admin.ModelAdmin):
    list_display = ("id", "crib", "user")


admin.site.register(Crib, CribAdmin)
admin.site.register(CribReply, CribReplyAdmin)
