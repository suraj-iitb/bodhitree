import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from course.models import Chapter, Section
from utils import mixins as custom_mixins
from utils.permissions import IsInstructorOrTA
from utils.utils import is_instructor_or_ta

from .models import Video
from .serializers import VideoSerializer


logger = logging.getLogger(__name__)


class VideoViewSet(
    viewsets.GenericViewSet,
    custom_mixins.IsRegisteredMixins,
):
    """Viewset for Video."""

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
            HTTP_400_BAD_REQUEST: Raised by:
                1. `is_valid()` method of the serializer
                2. If both or none section/chapter is provided
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by:
                1. If the user is not the instructor/ta of the course
                2. `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by:
                1. `_is_registered()` method
                2. Chapter/Section does not exist
        """
        user = request.user
        request_data = request.data

        # Validation logic such that only chapter/section is provided
        if request_data["section"] != "" and request_data["chapter"] != "":
            data = {"error": "Both chapter and section fields cannot be given."}
            logger.error(data["error"])
            return Response(data, status.HTTP_400_BAD_REQUEST)
        if request_data["section"] == "" and request_data["chapter"] == "":
            data = {"error": "Atleast one of chapter or section fields must be given"}
            logger.error(data["error"])
            return Response(data, status.HTTP_400_BAD_REQUEST)
        ##############################################################

        # Finds course id
        if request_data["chapter"] == "":
            section_id = request_data["section"]
            try:
                chapter_id = (
                    Section.objects.select_related("chapter")
                    .get(id=section_id)
                    .chapter.id
                )
            except Section.DoesNotExist as e:
                logger.exception(e)
                Response(e, status.HTTP_404_NOT_FOUND)
        else:
            chapter_id = request_data["chapter"]
        try:
            course_id = (
                Chapter.objects.select_related("course").get(id=chapter_id).course.id
            )
        except Chapter.DoesNotExist as e:
            logger.exception(e)
            Response(e, status.HTTP_404_NOT_FOUND)
        #################

        check = self._is_registered(course_id, user)
        if check is not True:
            return check

        # This is specifically done during video creation (not during updation or
        # deletion) because it can't be handled by IsInstructorOrTA permission class
        if not is_instructor_or_ta(course_id, user):
            data = {
                "error": "User: {} is not the instructor/ta of the "
                "course with id: {}".format(user, course_id),
            }
            logger.warning(data["error"])
            return Response(data, status.HTTP_403_FORBIDDEN)

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
            pk (int): chapter id

        Returns:
            `Response` with all the video data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered_using_chapter_id()` method
        """
        check, _ = self._is_registered_using_chapter_id(pk, request.user)
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
            pk (int): section id

        Returns:
            `Response` with all the video data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered_using_chapter_id()` method
        """
        check, _ = self._is_registered_using_section_id(pk, request.user)
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
            pk (int): video id

        Returns:
            `Response` with the video data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by:
                1. `_is_registered_using_chapter_id()` method
                2. `_is_registered_using_section_id()` method
        """
        user = request.user
        video = self.get_object()
        if video.chapter_id is None:
            check, course_id = self._is_registered_using_section_id(
                video.section_id, user
            )
        else:
            check, course_id = self._is_registered_using_chapter_id(
                video.chapter_id, user
            )
        if check is not True:
            return check

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
            HTTP_404_NOT_FOUND: Raised by:
                1. `_is_registered_using_chapter_id()` method
                2. `_is_registered_using_section_id()` method
        """
        user = request.user
        video = self.get_object()
        if video.chapter_id is None:
            check, course_id = self._is_registered_using_section_id(
                video.section_id, user
            )
        else:
            check, course_id = self._is_registered_using_chapter_id(
                video.chapter_id, user
            )
        if check is not True:
            return check

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
            pk (int): video id

        Returns:
            `Response` with no data and status HTTP_204_NO_CONTENT.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        user = request.user
        video = self.get_object()
        if video.chapter_id is None:
            check, course_id = self._is_registered_using_section_id(
                video.section_id, user
            )
        else:
            check, course_id = self._is_registered_using_chapter_id(
                video.chapter_id, user
            )
        if check is not True:
            return check

        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
