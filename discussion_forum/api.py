import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from utils import mixins as custom_mixins
from utils.pagination import StandardResultsSetPagination
from utils.permissions import IsInstructorOrTAOrStudent

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


class DiscussionThreadViewSet(
    viewsets.GenericViewSet, custom_mixins.IsRegisteredMixins
):
    """Viewset for `DiscussionThread`."""

    queryset = DiscussionThread.objects.all()
    serializer_class = DiscussionThreadSerializer
    permission_classes = (IsInstructorOrTAOrStudent,)
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=["POST"])
    def create_discussion_thread(self, request):
        """Adds a discussion thread to the discussion forum.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created discussion thread data and
             status HTTP_201_CREATED

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised by `DiscussionForum.DoesNotExist` exception
        """
        user = request.user
        discussion_forum_id = request.data["discussion_forum"]
        try:
            course_id = DiscussionForum.objects.get(id=discussion_forum_id).course_id
        except DiscussionForum.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        check = self._is_registered(course_id, user)
        if check is not True:
            return check

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"])
    def list_discussion_threads(self, request, pk):
        """Gets all the discussion threads in the discussion forum
           with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion_forum

        Returns:
            `Response` with all the discussion threads data
             and status HTTP_200_OK

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised by `DiscussionForum.DoesNotExist` exception
        """
        try:
            course_id = DiscussionForum.objects.get(id=pk).course_id
        except DiscussionForum.DoesNotExist as e:
            logger.exception(e)
            return Response(e, status.HTTP_404_NOT_FOUND)
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check

        discussion_threads = DiscussionThread.objects.filter(discussion_forum_id=pk)
        page = self.paginate_queryset(discussion_threads)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(discussion_threads, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_discussion_thread(self, request, pk):
        """Gets the discussion thread with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion thread

        Returns:
            `Response` with the discussion_thread data and status HTTP_200_OK

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTAOrStudent` permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        discussion_thread = self.get_object()
        serializer = self.get_serializer(discussion_thread)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_discussion_thread(self, request, pk):
        """Updates a discussion thread with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion thread

        Returns:
            `Response` with the updated discussion thread data and status HTTP_200_OK

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTAOrStudent` permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class DiscussionCommentViewSet(
    viewsets.GenericViewSet, custom_mixins.IsRegisteredMixins
):
    """Viewset for DiscussionComment."""

    queryset = DiscussionComment.objects.all()
    serializer_class = DiscussionCommentSerializer
    permission_classes = (IsInstructorOrTAOrStudent,)
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=["POST"])
    def create_discussion_comment(self, request):
        """Adds a discussion_comment to the discussion thread.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created discussion comment data and status
             HTTP_201_CREATED

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised by `DiscussionThread.DoesNotExist` exception
        """
        user = request.user
        discussion_thread_id = request.data["discussion_thread"]
        try:
            discussion_thread = DiscussionThread.objects.select_related(
                "discussion_forum"
            ).get(id=discussion_thread_id)
        except DiscussionThread.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        course_id = discussion_thread.discussion_forum.course.id
        check = self._is_registered(course_id, user)
        if check is not True:
            return check

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"])
    def list_discussion_comments(self, request, pk):
        """Gets all the discussion comments in the discussion thread with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion thread

        Returns:
            `Response` with all the discussion comment data and status HTTP_200_OK

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised by `DiscussionThread.DoesNotExist` exception
        """
        try:
            discussion_thread = DiscussionThread.objects.select_related(
                "discussion_forum"
            ).get(id=pk)
        except DiscussionThread.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)
        course_id = discussion_thread.discussion_forum.course_id
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check

        discussion_comments = DiscussionComment.objects.filter(discussion_thread=pk)
        page = self.paginate_queryset(discussion_comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(discussion_comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_discussion_comment(self, request, pk):
        """Gets the discussion comment with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion comment

        Returns:
            `Response` with the discussion comment data and status HTTP_200_OK

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTAOrStudent` permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        discussion_comment = self.get_object()
        serializer = self.get_serializer(discussion_comment)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_discussion_comment(self, request, pk):
        """Updates a discussion comment with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion thread

        Returns:
            `Response` with the updated discussion thread data and status HTTP_200_OK

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class DiscussionReplyViewSet(viewsets.GenericViewSet, custom_mixins.IsRegisteredMixins):
    """Viewset for DiscussionReply."""

    queryset = DiscussionReply.objects.all()
    serializer_class = DiscussionReplySerializer
    permission_classes = (IsInstructorOrTAOrStudent,)
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=["POST"])
    def create_discussion_reply(self, request):
        """Adds a discussion reply to the discussion comment.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created discussion reply data and status
             HTTP_201_CREATED

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised by `DiscussionComment.DoesNotExist` exception

        """
        user = request.user
        discussion_comment = request.data["discussion_comment"]
        try:
            discussion_comment = DiscussionComment.objects.select_related(
                "discussion_thread__discussion_forum"
            ).get(id=discussion_comment)
        except DiscussionComment.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        course_id = discussion_comment.discussion_thread.discussion_forum.course.id

        check = self._is_registered(course_id, user)
        if check is not True:
            return check

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"])
    def list_discussion_replies(self, request, pk):
        """Gets all the discussion replies in the discussion comment with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion comment

        Returns:
            `Response` with all the discussion replies data and status HTTP_200_OK

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised by `DiscussionComment.DoesNotExist` exception
        """
        try:
            discussion_comment = DiscussionComment.objects.select_related(
                "discussion_thread__discussion_forum"
            ).get(id=pk)
        except DiscussionComment.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        course_id = discussion_comment.discussion_thread.discussion_forum.course.id
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check

        discussion_replies = DiscussionReply.objects.filter(discussion_comment=pk)
        page = self.paginate_queryset(discussion_replies)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(discussion_replies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_discussion_reply(self, request, pk):
        """Gets the discussion reply with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion reply

        Returns:
            `Response` with the discussion reply data and status HTTP_200_OK

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTAOrStudent` permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        discussion_reply = self.get_object()
        serializer = self.get_serializer(discussion_reply)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_discussion_reply(self, request, pk):
        """Updates a discussion reply with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the discussion thread

        Returns:
            `Response` with the updated discussion thread data and status HTTP_200_OK

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
