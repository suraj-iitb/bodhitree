import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from course.models import Course
from utils.utils import check_course_registration

from .models import (
    DiscussionComment,
    DiscussionForum,
    DiscussionReply,
    DiscussionThread,
)
from .serializers import (
    DiscussionCommentSerializer,
    DiscussionReplySerializer,
    DiscussionThreadSerializer,
)


logger = logging.getLogger(__name__)


class DiscussionThreadViewSet(viewsets.GenericViewSet):
    """Viewset for DiscussionThread."""

    queryset = DiscussionThread.objects.all()
    serializer_class = DiscussionThreadSerializer
    filterset_fields = ("title",)
    search_fields = ("title",)
    ordering_fields = ("id",)

    def _is_registered(self, course_id, user):
        """Checks if the user is registered in the given course.

        Args:
            course_id (int): course id (pk)
            user (User): `User` model object

        Returns:
            A bool value representing whether the user is registered
            in the course with id course_id

        Raises:
            HTTP_404_NOT_FOUND: Raised if:
                1. The course does not exist
                2. The user is not registered in the course
        """
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            data = {
                "error": "Course with id: {} does not exist".format(course_id),
            }
            return Response(data, status.HTTP_404_NOT_FOUND)

        if not check_course_registration(course_id, user):
            data = {
                "error": "User: {} is not registered in the course: {}".format(
                    user, course
                ),
            }
            return Response(data, status.HTTP_404_NOT_FOUND)
        return True

    @action(detail=True, methods=["POST"])
    def create_discussion_thread(self, request, pk):
        """Adds a discussion_thread to the discussion_forum with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion_forum

        Returns:
            `Response` with the created discussion_thread data and
             status HTTP_201_CREATED

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        user = request.user
        check = self._is_registered(pk, user)
        if check is not True:
            return check

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["GET"])
    def list_discussion_threads(self, request, pk):
        """Gets all the discussion_threads in the discussion_forum
           with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion_forum

        Returns:
            `Response` with all the discussion_threads data
             and status HTTP_200_OK

        Raises:
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        check = self._is_registered(pk, request.user)
        if check is not True:
            return check
        discussion_threads = DiscussionThread.objects.filter(discussion_forum_id=pk)
        serializer = self.get_serializer(discussion_threads, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_discussion_thread(self, request, pk):
        """Gets the discussion_thread with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion_thread

        Returns:
            `Response` with the discussion_thread data and status HTTP_200_OK

        Raises:
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        discussion_thread = self.get_object()
        discussion_forum_id = discussion_thread.discussion_forum.id
        course_id = DiscussionForum.objects.get(id=discussion_forum_id).course.id
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check
        serializer = self.get_serializer(discussion_thread)
        return Response(serializer.data)

    def _discussion_thread_update_check(self, discussion_thread_id, user):
        """Checks if the user can update a discussion_thread

        Args:
            discussion_thread_id: discussion_thread id
            user (User): `User` model object

        Returns:
            A bool value representing whether the user can update a discussion_thread
        """
        try:
            discussion_thread = DiscussionThread.objects.select_related("author").get(
                id=discussion_thread_id
            )
        except DiscussionThread.DoesNotExist as e:
            logger.exception(e)
            data = {
                "error": "DiscussionThread with id: {} does not exist".format(
                    discussion_thread_id
                ),
            }
            return Response(data, status.HTTP_404_NOT_FOUND)

        if discussion_thread.author == user:
            return True
        data = {
            "error": """User: {} is not permitted to update the discussion
            thread with: {}""".format(
                user, discussion_thread_id
            ),
        }
        return Response(data, status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_discussion_thread(self, request, pk):
        """Updates a discussion_thread with id=pk."""
        check = self._discussion_thread_update_check(pk, request.user)
        if check is True:
            serializer = self.get_serializer(
                self.get_object(), data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        return check


class DiscussionCommentViewSet(viewsets.GenericViewSet):
    """Viewset for DiscussionComment."""

    queryset = DiscussionComment.objects.all()
    serializer_class = DiscussionCommentSerializer
    ordering_fields = ("id",)

    def _is_registered(self, course_id, user):
        """Checks if the user is registered in the given course.

        Args:
            course_id (int): course id (pk)
            user (User): `User` model object

        Returns:
            A bool value representing whether the user is registered
            in the course with id course_id

        Raises:
            HTTP_404_NOT_FOUND: Raised if:
                1. The course does not exist
                2. The user is not registered in the course
        """
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            data = {
                "error": "Course with id: {} does not exist".format(course_id),
            }
            return Response(data, status.HTTP_404_NOT_FOUND)

        if not check_course_registration(course_id, user):
            data = {
                "error": "User: {} is not registered in the course: {}".format(
                    user, course
                ),
            }
            return Response(data, status.HTTP_404_NOT_FOUND)
        return True

    @action(detail=True, methods=["POST"])
    def create_discussion_comment(self, request, pk):
        """Adds a discussion_comment to the discussion_thread with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion_thread

        Returns:
            `Response` with the created discussion_comment data and status
             HTTP_201_CREATED

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        user = request.user
        check = self._is_registered(pk, user)
        if check is not True:
            return check

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["GET"])
    def list_discussion_comments(self, request, pk):
        """Gets all the discussion_comment in the discussion_thread with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion_thread

        Returns:
            `Response` with all the discussion_comment data and status HTTP_200_OK

        Raises:
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        check = self._is_registered(pk, request.user)
        if check is not True:
            return check
        discussion_comments = DiscussionComment.objects.filter(discussion_thread_id=pk)
        serializer = self.get_serializer(discussion_comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_discussion_comment(self, request, pk):
        """Gets the discussion_comment with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion_comment

        Returns:
            `Response` with the discussion_comment data and status HTTP_200_OK

        Raises:
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        discussion_comment = self.get_object()
        discussion_thread = discussion_comment.discussion_thread.id
        discussion_forum_id = DiscussionThread.objects.get(
            id=discussion_thread
        ).discussion_forum.id
        course_id = DiscussionForum.objects.get(id=discussion_forum_id).course.id
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check
        serializer = self.get_serializer(discussion_comment)
        return Response(serializer.data)

    def _discussion_comment_update_check(self, discussion_comment_id, user):
        """Checks if the user can update a discussion_comment

        Args:
            discussion_comment_id: discussion_comment id
            user (User): `User` model object

        Returns:
            A bool value representing whether the user can update a discussion_comment
        """
        try:
            discussion_comment = DiscussionComment.objects.select_related("author").get(
                id=discussion_comment_id
            )
        except DiscussionComment.DoesNotExist as e:
            logger.exception(e)
            data = {
                "error": "DiscussionComment with id: {} does not exist".format(
                    discussion_comment_id
                ),
            }
            return Response(data, status.HTTP_404_NOT_FOUND)

        if discussion_comment.author == user:
            return True
        data = {
            "error": """User: {} is not permitted to update the discussion comment
            with: {}""".format(
                user, discussion_comment_id
            ),
        }
        return Response(data, status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_discussion_comment(self, request, pk):
        """Updates a discussion_thread with id=pk."""
        check = self._discussion_comment_update_check(pk, request.user)
        if check is True:
            serializer = self.get_serializer(
                self.get_object(), data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        return check


class DiscussionReplyViewSet(viewsets.GenericViewSet):
    """Viewset for DiscussionReply."""

    queryset = DiscussionReply.objects.all()
    serializer_class = DiscussionReplySerializer
    ordering_fields = ("id",)

    def _is_registered(self, course_id, user):
        """Checks if the user is registered in the given course.

        Args:
            course_id (int): course id (pk)
            user (User): `User` model object

        Returns:
            A bool value representing whether
            the user is registered
            in the course with id course_id

        Raises:
            HTTP_404_NOT_FOUND: Raised if:
                1. The course does not exist
                2. The user is not registered in the course
        """
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            data = {
                "error": "Course with id: {} does not exist".format(course_id),
            }
            return Response(data, status.HTTP_404_NOT_FOUND)

        if not check_course_registration(course_id, user):
            data = {
                "error": "User: {} is not registered in the course: {}".format(
                    user, course
                ),
            }
            return Response(data, status.HTTP_404_NOT_FOUND)
        return True

    @action(detail=True, methods=["POST"])
    def create_discussion_reply(self, request, pk):
        """Adds a discussion_reply to the discussion_comment with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion_comment

        Returns:
            `Response` with the created discussion_reply data and status
             HTTP_201_CREATED

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        user = request.user
        check = self._is_registered(pk, user)
        if check is not True:
            return check

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["GET"])
    def list_discussion_replies(self, request, pk):
        """Gets all the discussion_replies in the discussion_comment with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion_comment

        Returns:
            `Response` with all the discussion_replies
             data and status HTTP_200_OK

        Raises:
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        check = self._is_registered(pk, request.user)
        if check is not True:
            return check
        discussion_replies = DiscussionReply.objects.filter(discussion_comment_id=pk)
        serializer = self.get_serializer(discussion_replies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_discussion_reply(self, request, pk):
        """Gets the discussion_reply with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion_reply

        Returns:
            `Response` with the discussion_reply data and status HTTP_200_OK

        Raises:
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        discussion_reply = self.get_object()
        discussion_comment = discussion_reply.discussion_comment.id
        discussion_thread = DiscussionComment.objects.get(
            id=discussion_comment
        ).discussion_thread.id
        discussion_forum = DiscussionThread.objects.get(
            id=discussion_thread
        ).discussion_forum.id
        course_id = DiscussionForum.objects.get(id=discussion_forum).course.id
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check
        serializer = self.get_serializer(discussion_reply)
        return Response(serializer.data)

    def _discussion_reply_update_check(self, discussion_reply_id, user):
        """Checks if the user can update a discussion_reply

        Args:
            discussion_reply_id: discussion_reply id
            user (User): `User` model object

        Returns:
            A bool value representing whether the user can update a discussion_reply
        """
        try:
            discussion_reply = DiscussionReply.objects.select_related("author").get(
                id=discussion_reply_id
            )
        except DiscussionReply.DoesNotExist as e:
            logger.exception(e)
            data = {
                "error": "DiscussionReply with id: {} does not exist".format(
                    discussion_reply_id
                ),
            }
            return Response(data, status.HTTP_404_NOT_FOUND)

        if discussion_reply.author == user:
            return True
        data = {
            "error": """User: {} is not permitted to update the discussion
            reply with: {}""".format(
                user, discussion_reply_id
            ),
        }
        return Response(data, status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_discussion_reply(self, request, pk):
        """Updates a discussion_reply with id=pk."""
        check = self._discussion_reply_update_check(pk, request.user)
        if check is True:
            serializer = self.get_serializer(
                self.get_object(), data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        return check
