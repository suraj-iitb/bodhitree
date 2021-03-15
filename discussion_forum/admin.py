from django.contrib import admin

from discussion_forum.models import (DiscussionForum, Content, DiscussionThread, DiscussionComment, DiscussionReply, Tag, DiscussionThreadTag)


class DiscussionForumAdmin(admin.ModelAdmin):
    list_display = ('id', 'course')


class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content')

class DiscussionThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'discussion_forum')


class DiscussionCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'discussion_thread')

class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'discussion_comment')

class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'discussion_forum')


class DiscussionThreadTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'discussion_thread')


admin.site.register(DiscussionForum, DiscussionForumAdmin)
admin.site.register(Content, ContentAdmin)
admin.site.register(DiscussionThread, DiscussionThreadAdmin)
admin.site.register(DiscussionComment, DiscussionCommentAdmin)
admin.site.register(DiscussionReply, DiscussionReplyAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(DiscussionThreadTag, DiscussionThreadTagAdmin)

