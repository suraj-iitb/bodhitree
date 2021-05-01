from django.urls import include, path
from rest_framework import routers

from .api import (
    DiscussionCommentViewSet,
    DiscussionReplyViewSet,
    DiscussionThreadViewSet,
)


app_name = "discussion_forum"

router = routers.DefaultRouter()
router.register(r"discussion_threads", DiscussionThreadViewSet)
router.register(r"discussion_comments", DiscussionCommentViewSet)
router.register(r"discussion_replies", DiscussionReplyViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
