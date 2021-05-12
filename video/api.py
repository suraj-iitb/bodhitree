import logging

from rest_framework import viewsets
from rest_framework.decorators import action

from utils import mixins as custom_mixins
from utils.permissions import IsInstructorOrTA

from .models import Video
from .serializers import VideoSerializer


logger = logging.getLogger(__name__)


class VideoViewSet(
    viewsets.GenericViewSet,
    custom_mixins.ContentMixin_Create,
    custom_mixins.ContentMixin_List,
    custom_mixins.RetrieveMixin,
    custom_mixins.DeleteMixin,
    custom_mixins.UpdateMixin,
):
    """Viewset for `Video`."""

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = (IsInstructorOrTA,)

    @action(detail=False, methods=["POST"])
    def create_video(self, request):
        return self.create_content(request)

    @action(detail=True, methods=["GET"])
    def list_chapter_videos(self, request, pk):
        return self.list_chapter_content(request, pk, Video)

    @action(detail=True, methods=["GET"])
    def list_section_videos(self, request, pk):
        return self.list_section_content(request, pk, Video)

    @action(detail=True, methods=["GET"])
    def retrieve_video(self, request, pk):
        return self.retrieve(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_video(self, request, pk):
        return self.update(request, pk)

    @action(detail=True, methods=["DELETE"])
    def delete_video(self, request, pk):
        return self._delete(request, pk)
