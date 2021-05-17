import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from course.models import CourseHistory
from utils import mixins as custom_mixins
from utils.permissions import IsInstructorOrTA

from .models import AdvancedProgrammingAssignment, SimpleProgrammingAssignment
from .serializers import (
    AdvancedProgrammingAssignmentSerializer,
    SimpleProgrammingAssignmentSerializer,
)


logger = logging.getLogger(__name__)


class AssignmentMixin(
    custom_mixins.InsOrTACreateMixin,
    custom_mixins.InsOrTAListMixin,
    custom_mixins.RetrieveMixin,
    custom_mixins.UpdateMixin,
    custom_mixins.DeleteMixin,
):
    """Common mixin for `SimpleProgrammingAssignmentViewSet()` and
    `AdvancedProgrammingAssignmentViewSet()`."""

    def date_check(self, start_date, end_date):
        if start_date > end_date:
            error = "Schedule end date has to be greater than start date"
            logger.error(error)
            return Response(error, status.HTTP_400_BAD_REQUEST)
        return True

    def create_assign(self, request):
        """Adds an assignment to the course.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created assignment data and status `HTTP_201_CREATED`

        Raises:
            `HTTP_400_BAD_REQUEST`: Raised due to `create()` method
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTA` permission
                class
            `HTTP_403_FORBIDDEN`: Raised due to `create()` method
            `HTTP_404_NOT_FOUND`: Raised due to `create()` method
        """

        start_date = request.data["start_date"]
        end_date = request.data["end_date"]
        extended_date = request.data["extended_date"]

        if self.date_check(start_date, end_date) and self.date_check(
            end_date, extended_date
        ):
            course_id = request.data["course"]
            return self.create(request, course_id)
        errors = """End date should be greater than start date.
            Extended date should be greater than end date."""
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def list_assign(self, request, pk):
        """Gets all the assignment in the current course.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with all the assignment data and status `HTTP_200_OK`

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTA` permission class
            `HTTP_403_FORBIDDEN`: Raised due to `list()` method
            `HTTP_404_NOT_FOUND`: Raised due to `list()` method
        """
        return self.list(request, pk)

    def list_assign_stud(self, request, pk):
        """Gets all the published assignment to the registered student in the current course.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with all the assignment data and status `HTTP_200_OK`

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTA` permission class
            `HTTP_403_FORBIDDEN`: Raised due to `_is_registered()` method
            `HTTP_404_NOT_FOUND`: Raised due to `_is_registered()` method
        """
        user = request.user
        check = self._is_registered(pk, user)
        if check is not True:
            return check
        assignments = SimpleProgrammingAssignment.objects.filter(
            course=pk, is_published=True
        )

        page = self.paginate_queryset(assignments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)

    def retrieve_assign(self, request, pk):
        """Gets the assignment with primary key as pk to the instructor.
           Gets the assignment with primary key as pk, only if published to the student.

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the assignment

        Returns:
            `Response` with the assignment data and status `HTTP_200_OK`

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by:
                1.`IsInstructorOrTA` permission class
            `HTTP_403_FORBIDDEN`:  Raised:
                1. If student is trying to access an unpublished assignment
            `HTTP_404_NOT_FOUND`: Raised by `get_object()` method
        """
        user = request.user
        assignment = self.get_object()
        if CourseHistory.objects.get(user=user, course=assignment.course).role == "S":
            if assignment.is_published is True:
                serializer = self.get_serializer(assignment)
                return Response(serializer.data)
            else:
                return Response(
                    "You are not allowed to view this assignment",
                    status.HTTP_403_FORBIDDEN,
                )
        serializer = self.get_serializer(assignment)
        return Response(serializer.data)

    def update_assign(self, request, pk):
        """Updates an assignment of the course..

        Args:
            request (Request): DRF `Request` object
            pk (int): Primary key of the assignment

        Returns:
            `Response` with the updated assignment data and status `HTTP_200_OK`

        Raises:
            `HTTP_400_BAD_REQUEST`: Raised:
                1. `update()` method
                2. if start date is greater than end date/ end date is greater than
                   extended date
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTA` permission
                class
            `HTTP_403_FORBIDDEN`: Raised
                1. by `IsInstructorOrTA` permission class
            `HTTP_404_NOT_FOUND`: Raised by `update()` method
        """
        start_date = request.data["start_date"]
        end_date = request.data["end_date"]
        extended_date = request.data["extended_date"]

        if self.date_check(start_date, end_date) and self.date_check(
            end_date, extended_date
        ):
            return self.update(request, pk)
        errors = """End date should be greater than start date.
            Extended date should be greater than end date."""
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_assign(self, request, pk):
        """Deletes the assignment with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): assignment id

        Returns:
            `Response` with no data and status HTTP_204_NO_CONTENT.

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTA` permission class
            `HTTP_403_FORBIDDEN`: Raised by `IsInstructorOrTA` permission class
            `HTTP_404_NOT_FOUND`: due to `_delete()` method
        """
        return self._delete(request, pk)


class SimpleProgrammingAssignmentViewSet(viewsets.GenericViewSet, AssignmentMixin):
    """Viewset for `SimpleProgrammingAssignment()`."""

    queryset = SimpleProgrammingAssignment.objects.all()
    serializer_class = SimpleProgrammingAssignmentSerializer
    permission_classes = (IsInstructorOrTA,)

    def get_queryset_list(self, course_id):
        queryset = SimpleProgrammingAssignment.objects.filter(course=course_id)
        return queryset

    @action(detail=False, methods=["POST"])
    def create_assignment(self, request):
        return self.create_assign(request)

    @action(detail=True, methods=["GET"])
    def list_assignments(self, request, pk):
        return self.list_assign(request, pk)

    @action(detail=True, methods=["GET"])
    def list_assignments_stud(self, request, pk):
        return self.list_assign_stud(request, pk)

    @action(
        detail=True,
        methods=["GET"],
    )
    def retrieve_assignment(self, request, pk):
        return self.retrieve_assign(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_assignment(self, request, pk):
        return self.update_assign(request, pk)

    @action(detail=True, methods=["DELETE"])
    def delete_assignment(self, request, pk):
        return self.delete_assign(request, pk)


class AdvancedProgrammingAssignmentViewSet(viewsets.GenericViewSet, AssignmentMixin):
    """Viewset for `AdvancedProgrammingAssignment()`."""

    queryset = AdvancedProgrammingAssignment.objects.all()
    serializer_class = AdvancedProgrammingAssignmentSerializer
    permission_classes = (IsInstructorOrTA,)

    def get_queryset_list(self, course_id):
        queryset = AdvancedProgrammingAssignment.objects.filter(course=course_id)
        return queryset

    @action(detail=False, methods=["POST"])
    def create_assignment(self, request):
        return self.create_assign(request)

    @action(detail=True, methods=["GET"])
    def list_assignments(self, request, pk):
        return self.list_assign(request, pk)

    @action(detail=True, methods=["GET"])
    def list_assignments_stud(self, request, pk):
        return self.list_assign_stud(request, pk)

    @action(
        detail=True,
        methods=["GET"],
    )
    def retrieve_assignment(self, request, pk):
        return self.retrieve_assign(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_assignment(self, request, pk):
        return self.update_assign(request, pk)

    @action(detail=True, methods=["DELETE"])
    def delete_assignment(self, request, pk):
        return self.delete_assign(request, pk)
