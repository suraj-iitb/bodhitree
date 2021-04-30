from django.urls import include, path
from rest_framework import routers

from .api import (
    DiscussionCommentViewSet,
    DiscussionReplyViewSet,
    DiscussionThreadViewSet,
)


app_name = "discussion_forum"

router = routers.DefaultRouter()
router.register(r"discussionthreads", DiscussionThreadViewSet)
router.register(r"discussioncomments", DiscussionCommentViewSet)
router.register(r"discussionreplies", DiscussionReplyViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
