import logging

from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from utils.drf_utils import UserPermission

from .models import User
from .serializers import UserSerializer


logger = logging.getLogger(__name__)


class UserViewSet(viewsets.GenericViewSet):
    """Viewset for User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserPermission,)
    filterset_fields = (
        "email",
        "full_name",
        "is_active",
    )
    search_fields = ("email", "full_name", "is_active")
    ordering_fields = ("id",)

    @action(detail=False, methods=["POST"])
    def create_user(self, request):
        """Adds a user.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created user data and status HTTP_201_CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_403_FORBIDDEN: Raised by `IntegrityError` of the database
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                return Response(e, status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"])
    def logout(self, request, pk=None):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.exception(e)
            return Response(e, status=status.HTTP_400_BAD_REQUEST)
