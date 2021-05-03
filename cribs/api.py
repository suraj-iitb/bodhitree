import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from course.models import CourseHistory
from utils import mixins as custom_mixins
from utils.drf_utils import (
    IsInstructorOrTA,
    IsInstructorOrTAOrStudent,
    IsOwner,
    StandardResultsSetPagination,
)

from .models import Crib
from .serializers import CribSerializer


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
        """.
        Args:
            request (Request): DRF `Request` object
        Returns:
            `Response` with the created crib data and
             status HTTP_201_CREATED
        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTAOrStudent` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
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

    @action(detail=True, methods=["GET"], permission_classes=[IsInstructorOrTA])
    def list_cribs(self, request, pk):
        """Gets all the cribs in the current course
           with primary key as pk.
        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the course
        Returns:
            `Response` with all the cribs data
             and status HTTP_200_OK
        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTAOrStudent` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        cribs = Crib.objects.select_related("course").filter(course_id=pk)
        course_id = cribs[0].course.id
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check

        page = self.paginate_queryset(cribs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(cribs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_crib(self, request, pk):
        """Gets the crib with primary key as pk.
        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the crib
        Returns:
            `Response` with the crib data and status HTTP_200_OK
        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTAOrStudent` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        crib = Crib.objects.select_related("course").get(id=pk)
        course_id = crib.course.id
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check
        else:
            try:
                course_history = CourseHistory.objects.select_related("role").get(
                    user=crib.created_by
                )
            except CourseHistory.DoesNotExist:
                if course_history.role != "S":
                    pass
                else:
                    data = {
                        "error": "User: {} is not the creator of the crib: {}".format(
                            course_history.user, course_history.course
                        ),
                    }
                    logger.error(data["errors"])
                    return Response(data, status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(crib)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"], permission_classes=[IsOwner])
    def update_crib(self, request, pk):
        """Updates a crib with id as pk.
        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the crib
        Returns:
            `Response` with the updated crib data and status HTTP_200_OK
        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTAOrStudent` permission class
            HTTP_404_NOT_FOUND: Raised:
                1. By `_is_registered()` method
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
