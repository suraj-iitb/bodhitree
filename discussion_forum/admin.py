from django.contrib import admin

from discussion_forum.models import (
    Content,
    DiscussionComment,
    DiscussionForum,
    DiscussionReply,
    DiscussionThread,
    Tag,
)


class DiscussionForumAdmin(admin.ModelAdmin):
    list_display = ("id", "course")
    search_fields = ("course__title",)


class ContentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "description")
    search_fields = ("user__email", "description")


class DiscussionThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "discussion_forum")
    search_fields = ("content__description",)


class DiscussionCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "discussion_thread")
    search_fields = ("content__description",)


class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "discussion_comment")
    search_fields = ("content__description",)


class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "discussion_forum", "tag_name")
    search_fields = ("content__description", "tag_name")


admin.site.register(DiscussionForum, DiscussionForumAdmin)
admin.site.register(Content, ContentAdmin)
admin.site.register(DiscussionThread, DiscussionThreadAdmin)
admin.site.register(DiscussionComment, DiscussionCommentAdmin)
admin.site.register(DiscussionReply, DiscussionReplyAdmin)
admin.site.register(Tag, TagAdmin)
