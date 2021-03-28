from django.contrib import admin

from cribs.models import Crib, CribReply


class CribAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "created_by",
        "assigned_to",
        "title",
        "description",
        "status",
        "created_on",
    )
    search_fields = (
        "title",
        "description",
    )


class CribReplyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "crib",
        "user",
        "description",
        "created_on",
    )
    search_fields = ("description",)


admin.site.register(Crib, CribAdmin)
admin.site.register(CribReply, CribReplyAdmin)
