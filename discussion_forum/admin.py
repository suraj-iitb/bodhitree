from django.contrib import admin

from discussion_forum.models import (
    DiscussionComment,
    DiscussionForum,
    DiscussionReply,
    DiscussionThread,
    Tag,
)


class DiscussionForumAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "anonymous_to_instructor",
        "send_email_to_all",
    )
    search_fields = ("course__title",)


class DiscussionThreadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "author_category",
        "title",
        "description",
        "pinned",
        "anonymous_to_student",
        "upvote",
        "downvote",
        "created_on",
        "modified_on",
        "discussion_forum",
        "mark_as_important",
    )
    search_fields = (
        "title",
        "description",
    )


class DiscussionCommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "author_category",
        "description",
        "pinned",
        "anonymous_to_student",
        "upvote",
        "downvote",
        "created_on",
        "modified_on",
        "discussion_thread",
    )
    search_fields = ("description",)


class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "author_category",
        "description",
        "pinned",
        "anonymous_to_student",
        "upvote",
        "downvote",
        "created_on",
        "modified_on",
        "discussion_comment",
    )
    search_fields = ("description",)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "discussion_forum",
        "content_id",
        "content_type",
        "tag_name",
    )
    search_fields = ("tag_name",)


admin.site.register(DiscussionForum, DiscussionForumAdmin)
admin.site.register(DiscussionThread, DiscussionThreadAdmin)
admin.site.register(DiscussionComment, DiscussionCommentAdmin)
admin.site.register(DiscussionReply, DiscussionReplyAdmin)
admin.site.register(Tag, TagAdmin)
