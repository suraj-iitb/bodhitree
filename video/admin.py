from django.contrib import admin

from .models import QuizMarker, SectionMarker, Video, VideoHistory


class VideoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chapter",
        "section",
        "title",
        "description",
        "video_file",
        "doc_file",
        "in_video_quiz_file",
        "video_duration",
        "uploaded_on",
        "modified_on",
    )
    search_fields = ("title",)


class VideoHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "video", "user", "video_watched_duration")
    search_fields = ("video__title", "user__email")


class SectionMarkerAdmin(admin.ModelAdmin):
    list_display = ("id", "video", "time", "title", "created_on", "modified_on")
    search_fields = ("video__title", "title")


class QuizMarkerAdmin(admin.ModelAdmin):
    list_display = ("id", "video", "time", "title", "quiz", "created_on", "modified_on")
    search_fields = ("video__title", "title")


admin.site.register(Video, VideoAdmin)
admin.site.register(VideoHistory, VideoHistoryAdmin)
admin.site.register(SectionMarker, SectionMarkerAdmin)
admin.site.register(QuizMarker, QuizMarkerAdmin)
