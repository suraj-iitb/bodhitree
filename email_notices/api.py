import logging

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from utils import mixins as custom_mixins
from utils.permissions import IsInstructorOrTA

from .models import Email
from .serializers import EmailSerializer


logger = logging.getLogger(__name__)


class EmailViewSet(
    viewsets.GenericViewSet,
    custom_mixins.InsOrTACreateMixin,
    custom_mixins.RetrieveMixin,
):
    """Viewset for `Email`."""

    queryset = Email.objects.all()
    serializer_class = EmailSerializer
    permission_classes = (IsInstructorOrTA,)

    @action(detail=False, methods=["POST"])
    def create_email(self, request):
        """Adds an email to the course.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created email data and status `HTTP_201_CREATED`

        Raises:
            `HTTP_400_BAD_REQUEST`: Raised due to `create()` method
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTA` permission
                class
            `HTTP_403_FORBIDDEN`: Raised due to `create()` method
            `HTTP_404_NOT_FOUND`: Raised due to `create()` method
        """
        course_id = request.data["course"]
        return self.create(request, course_id)

    @action(detail=True, methods=["GET"])
    def list_emails_instructor(self, request, pk):
        """Gets all the email in the current course.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with all the email data and status `HTTP_200_OK`

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTA` permission class
            `HTTP_403_FORBIDDEN`: Raised due to `_is_instructor_or_ta()` method
            `HTTP_404_NOT_FOUND`: Raised due to `_is_instructor_or_ta()` method
        """
        user = request.user
        check = self._is_instructor_or_ta(pk, user)
        if check is not True:
            return check
        emails = Email.objects.filter(course=pk)

        page = self.paginate_queryset(emails)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(emails, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def list_emails_student(self, request, pk):
        """Gets the emails in the current course and those in which the student is a recipient.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with all the email data and status `HTTP_200_OK`

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTA` permission class
            `HTTP_403_FORBIDDEN`: Raised due to `_is_registered()` method
            `HTTP_404_NOT_FOUND`: Raised due to `_is_registered()` method
        """
        user = request.user
        check = self._is_registered(pk, user)
        if check is not True:
            return check
        emails = Email.objects.filter(course=pk, to_email_list__contains=[user.email])

        page = self.paginate_queryset(emails)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(emails, many=True)
        return Response(serializer.data)
