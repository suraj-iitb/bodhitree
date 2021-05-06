import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from course.models import Chapter, Section
from utils import mixins as custom_mixins
from utils.permissions import IsInstructorOrTA

from .models import Video
from .serializers import VideoSerializer


logger = logging.getLogger(__name__)


class VideoViewSet(viewsets.GenericViewSet, custom_mixins.IsRegisteredMixins):
    """Viewset for `Video`."""

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = (IsInstructorOrTA,)

    @action(detail=False, methods=["POST"])
    def create_video(self, request):
        """Adds a video to the chapter/section

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created video data and status HTTP_201_CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Raised:
                1. By `is_valid()` method of the serializer
                2. If both (or none) the section/chapter is provided
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `_is_instructor_or_ta()` method
            HTTP_404_NOT_FOUND: Raised if chapter/section does not exist
        """
        user = request.user
        request_data = request.data

        # Validation logic such that only chapter/section is provided. It is done by
        # serializer during validation but we are doing it here becuase we require
        # course_id using chapter/section to check for instructor/ta.
        if request_data["section"] == "" and request_data["chapter"] == "":
            error = "Atleast one of field (chapter or section) must be given."
            logger.error(error)
            return Response(error, status.HTTP_400_BAD_REQUEST)
        elif request_data["section"] != "" and request_data["chapter"] != "":
            error = "Both fields (chapter and section) must not be given."
            logger.error(error)
            return Response(error, status.HTTP_400_BAD_REQUEST)

        # Finds course id
        if request_data["chapter"] == "":
            section_id = request_data["section"]
            try:
                chapter_id = Section.objects.get(id=section_id).chapter_id
            except Section.DoesNotExist as e:
                logger.exception(e)
                return Response(str(e), status.HTTP_404_NOT_FOUND)
        else:
            chapter_id = request_data["chapter"]
        try:
            chapter = Chapter.objects.get(id=chapter_id)
        except Chapter.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)
        course_id = chapter.course_id

        # This is specifically done during video creation (not during updation or
        # deletion) because it can't be handled by `IsInstructorOrTA` permission class.
        check = self._is_instructor_or_ta(course_id, user)
        if check is not True:
            return check

        serializer = self.get_serializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"])
    def list_chapter_videos(self, request, pk):
        """Gets all the videos in the chapter with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Chapter id

        Returns:
            `Response` with all the video data in chapter and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised if the chapter does not exist
        """
        try:
            course_id = Chapter.objects.get(id=pk).course_id
        except Chapter.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check

        videos = Video.objects.filter(chapter_id=pk)
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def list_section_videos(self, request, pk):
        """Gets all the videos in the section with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Section id

        Returns:
            `Response` with all the video data in section and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised if the section does not exist
        """
        try:
            course_id = (
                Section.objects.select_related("chapter").get(id=pk).chapter.course_id
            )
        except Section.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check

        videos = Video.objects.filter(section_id=pk)
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_video(self, request, pk):
        """Gets the video with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Video id

        Returns:
            `Response` with the video data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        video = self.get_object()
        serializer = self.get_serializer(video)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_video(self, request, pk):
        """Updates the video with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): video id

        Returns:
            `Response` with the updated video data and status HTTP_200_OK.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        video = self.get_object()
        serializer = self.get_serializer(video, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["DELETE"])
    def delete_video(self, request, pk):
        """Deletes the video with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Video id

        Returns:
            `Response` with no data and status HTTP_204_NO_CONTENT.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        video = self.get_object()
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
