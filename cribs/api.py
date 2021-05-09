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
    custom_mixins.CreateMixin_Reg,
    custom_mixins.ListMixin_InsOrTA_Paginated,
    custom_mixins.RetrieveMixin,
    custom_mixins.UpdateMixin,
):
    """Viewset for `Crib`."""

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
            `Response` with the created crib data and status `HTTP_201_CREATED`

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrStudent` permission
                class
            `HTTP_404_NOT_FOUND`: Raised by `Course.DoesNotExist` exception
        """
        course_id = request.data["course"]
        return self.create(request, course_id)

    @action(detail=True, methods=["GET"])
    def list_cribs(self, request, pk):
        """Gets all the cribs in the current course.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with all the cribs data and status `HTTP_200_OK`

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrStudent` permission
                class
        """
        return self.list(request, pk, Crib)

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
            `Response` with the crib data and status `HTTP_200_OK`

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by:
                1.`StrictIsInstructorOrTA` permission class
                2.`IsOwner` permission class
            `HTTP_403_FORBIDDEN`:  Raised by:
                1.`StrictIsInstructorOrTA` permission class
                2.`IsOwner` permission class
        """
        return self.retrieve(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"], permission_classes=[IsOwner])
    def update_crib(self, request, pk):
        """Updates a crib.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the crib

        Returns:
            `Response` with the updated crib data and status `HTTP_200_OK`

        Raises:
            `HTTP_401_UNAUTHORIZED`:  Raised by `IsOwner` permission class
            `HTTP_403_FORBIDDEN`: Raised by `IsOwner` permission class
        """
        return self.update(request, pk)


class CribReplyViewSet(
    viewsets.GenericViewSet,
    custom_mixins.CreateMixin_Reg,
    custom_mixins.RetrieveMixin,
    custom_mixins.UpdateMixin,
):
    """Viewset for `CribReply`."""

    queryset = CribReply.objects.all()
    serializer_class = CribReplySerializer
    permission_classes = (IsInstructorOrTAOrStudent,)
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=["POST"])
    def create_crib_reply(self, request):
        """Adds a crib reply to the crib.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created crib reply data and status `HTTP_201_CREATED`

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrStudent` permission
                class
            `HTTP_404_NOT_FOUND`: Raised by `Crib.DoesNotExist` exception
        """
        crib = request.data["crib"]

        try:
            course_id = Crib.objects.get(id=crib).course_id
        except Crib.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)
        return self.create(request, course_id)

    @action(detail=True, methods=["GET"], permission_classes=[IsOwner])
    def list_crib_replies(self, request, pk):
        """Gets all the crib replies of the current crib.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the crib id

        Returns:
            `Response` with all the cribs data and status `HTTP_200_OK`

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrStudent` permission
                 class
            `HTTP_403_FORBIDDEN`: Raised by
                1.`_is_instructor_or_ta` method
                2. Non-owner student
            `HTTP_404_NOT_FOUND`: Raised by `Crib.DoesNotExist` exception
        """
        try:
            crib = Crib.objects.get(id=pk)
        except Crib.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        check = self._is_instructor_or_ta(crib.course, request.user)
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
            `Response` with the crib reply data and status `HTTP_200_OK`

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by:
                1.`StrictIsInstructorOrTA` permission class
                2.`IsOwner` permission class
            `HTTP_403_FORBIDDEN`: Raised by:
                1.`StrictIsInstructorOrTA` permission class
                2.`IsOwner` permission class
        """
        return self.retrieve(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"], permission_classes=[IsOwner])
    def update_crib_reply(self, request, pk):
        """Updates a crib reply.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the crib reply

        Returns:
            `Response` with the updated crib data and status `HTTP_200_OK`

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsOwner` permission
                class
            `HTTP_403_FORBIDDEN`: Raised by `IsOwner` permission class
        """
        return self.update(request, pk)
