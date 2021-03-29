from django.contrib import admin

from .models import Document


class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "section",
        "chapter",
        "title",
        "description",
        "doc_file",
        "created_on",
        "modified_on",
    )
    search_fields = (
        "title",
        "description",
    )


admin.site.register(Document, DocumentAdmin)
