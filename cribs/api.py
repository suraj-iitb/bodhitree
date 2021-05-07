import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from utils import mixins as custom_mixins
from utils.pagination import StandardResultsSetPagination
from utils.permissions import IsInstructorOrTAOrStudent, IsOwner, StrictIsInstructorOrTA

from .models import Crib, CribReply
from .serializers import CribReplySerializer, CribSerializer


logger = logging.getLogger(__name__)


class CribViewSet(
    viewsets.GenericViewSet,
    custom_mixins.IsRegisteredMixins,
):
    """Viewset for Crib."""

    queryset = Crib.objects.all()
    serializer_class = CribSerializer
    permission_classes = (IsInstructorOrTAOrStudent,)
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=["POST"])
    def create_crib(self, request):
        """Adds a crib to the course.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created crib data and
             status HTTP_201_CREATED

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
        """
        user = request.user
        course_id = request.data["course"]
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
    def list_cribs(self, request, pk):
        """Gets all the cribs in the current course.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with all the cribs data
             and status HTTP_200_OK

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `_is_instructor_or_ta` method
        """
        check = self._is_instructor_or_ta(pk, request.user)
        if check is not True:
            return check

        cribs = Crib.objects.filter(course_id=pk)
        page = self.paginate_queryset(cribs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(cribs, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[StrictIsInstructorOrTA | IsOwner],
    )
    def retrieve_crib(self, request, pk):
        """Gets the crib with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the crib

        Returns:
            `Response` with the crib data and status HTTP_200_OK

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by:
                1.`IsInstructorOrTAOrStudent` permission class
                2.`IsOwner` permission class
            HTTP_403_FORBIDDEN: Raised by `IsOwner` permission class
        """
        crib = self.get_object()
        serializer = self.get_serializer(crib)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"], permission_classes=[IsOwner])
    def update_crib(self, request, pk):
        """Updates a crib.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the crib

        Returns:
            `Response` with the updated crib data and status HTTP_200_OK

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of serializer
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsOwner` permission class
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


class CribReplyViewSet(
    viewsets.GenericViewSet,
    custom_mixins.IsRegisteredMixins,
):
    """Viewset for CribReply."""

    queryset = CribReply.objects.all()
    serializer_class = CribReplySerializer
    permission_classes = (IsInstructorOrTAOrStudent,)
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=["POST"])
    def create_crib_reply(self, request):
        """Adds a crib reply to the course.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created crib reply data and
             status HTTP_201_CREATED

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
        """
        user = request.user
        crib = request.data["crib"]
        course_id = Crib.objects.get(id=crib).course_id
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

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[IsOwner],
    )
    def list_crib_replies(self, request, pk):
        """Gets all the crib replies of the current crib.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the crib id

        Returns:
            `Response` with all the cribs data
             and status HTTP_200_OK

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `_is_instructor_or_ta` method
        """
        try:
            crib = Crib.objects.get(id=pk)
        except Crib.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        print("11111111111111111111111111111111111111")
        print(crib.course, request.user)
        check = self._is_instructor_or_ta(crib.course, request.user)
        print("---------------------------------")
        print(check)
        if (check is True) or request.user == crib.created_by:
            cribreplies = CribReply.objects.filter(crib_id=pk)
            page = self.paginate_queryset(cribreplies)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(cribreplies, many=True)
            return Response(serializer.data)
        error = "You are not allowed to view this crib."
        logger.error(error)
        return Response(error, status.HTTP_403_FORBIDDEN)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[StrictIsInstructorOrTA | IsOwner],
    )
    def retrieve_crib_reply(self, request, pk):
        """Gets the crib reply with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the crib reply

        Returns:
            `Response` with the crib reply data and status HTTP_200_OK

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by:
                1.`IsInstructorOrTAOrStudent` permission class
                2.`IsOwner` permission class
            HTTP_403_FORBIDDEN: Raised by `IsOwner` permission class
        """
        cribreply = self.get_object()
        serializer = self.get_serializer(cribreply)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"], permission_classes=[IsOwner])
    def update_crib_reply(self, request, pk):
        """Updates a crib reply.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the crib reply

        Returns:
            `Response` with the updated crib data and status HTTP_200_OK

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of serializer
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsOwner` permission class
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
