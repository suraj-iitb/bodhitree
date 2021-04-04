from django.db.models import Q
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination

from course.models import CourseHistory


class StandardResultsSetPagination(PageNumberPagination):
    """
    Pagination class for DEFAULT_PAGINATION_CLASS rest_framework settings.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class IsInstructorOrTAOrReadOnly(permissions.BasePermission):
    """
    Allows complete permission to instructor/ta and access to others
    """

    def has_permission(self, request, view):

        """
        Returns whether user has permission on this model or not
        """

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        """
        Returns whether user has permission on this object or not
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            course_histories = CourseHistory.objects.filter(
                Q(course=obj) & (Q(role="I") | Q(role="T"))
            )
            for course_history in course_histories:
                if course_history.user == request.user:
                    return True
            return False
