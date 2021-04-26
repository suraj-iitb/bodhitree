from django.db.models import Q
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination

from course.models import (
    Announcement,
    Chapter,
    CourseHistory,
    Notification,
    Page,
    Schedule,
    Section,
)
from cribs.models import Crib
from discussion_forum.models import (
    DiscussionComment,
    DiscussionForum,
    DiscussionReply,
    DiscussionThread,
)
from document.models import Document
from email_notices.models import Email
from programming_assignments.models import (
    AdvancedProgrammingAssignment,
    AdvancedProgrammingAssignmentHistory,
    AssignmentSection,
    Exam,
    SimpleProgrammingAssignment,
    SimpleProgrammingAssignmentHistory,
    Testcase,
)
from quiz.models import (
    DescriptiveQuestion,
    FixedAnswerQuestion,
    MultipleCorrectQuestion,
    QuestionModule,
    Quiz,
    SingleCorrectQuestion,
)
from subjective_assignments.models import (
    SubjectiveAssignment,
    SubjectiveAssignmentHistory,
)
from utils.utils import is_instructor_or_ta
from video.models import QuizMarker, SectionMarker, Video


class StandardResultsSetPagination(PageNumberPagination):
    """Pagination class for viewsets."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class IsInstructorOrTA(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for: Chapter, Section, Video, Document, Quiz, SectionMarker, QuizMarker,
                    QuestionModule, SingleCorrectQuestion, MultipleCorrectQuestion,
                    FixedAnswerQuestion, DescriptiveQuestion, Schedule, Page,
                    Announcement, Notification, DiscussionForum,
                    SimpleProgrammingAssignment, AdvancedProgrammingAssignment,
                    AssignmentSection, Testcase, Exam, SubjectiveAssignment

    Allows:
        1. complete permissions to instructor/ta
        2. list/retrieve permissions to students
    """

    def _get_course_from_object(self, obj):
        """get course using obj instance

        Args:
            obj : Model object (like Chapter, Quiz)

        Returns:
            course: Course model object
        """
        if type(obj) in (Video, Document, Quiz):
            course = obj.chapter.course if obj.chapter else obj.section.chapter.course
        elif type(obj) in (SectionMarker, QuizMarker):
            course = (
                obj.video.chapter.course
                if obj.video.chapter
                else obj.video.section.chapter.course
            )
        elif type(obj) == QuestionModule:
            course = (
                obj.quiz.chapter.course
                if obj.quiz.chapter
                else obj.quiz.section.chapter.course
            )
        elif type(obj) in (
            SingleCorrectQuestion,
            MultipleCorrectQuestion,
            FixedAnswerQuestion,
            DescriptiveQuestion,
        ):
            course = (
                obj.question_module.quiz.chapter.course
                if obj.question_module.quiz.chapter
                else obj.question_module.quiz.section.chapter.course
            )
        elif type(obj) in (
            Chapter,
            Schedule,
            Announcement,
            Page,
            Notification,
            DiscussionForum,
            Email,
        ):
            course = obj.course
        elif type(obj) == Section:
            course = obj.chapter.course
        elif type(obj) in (
            SimpleProgrammingAssignment,
            AssignmentSection,
            Exam,
            SubjectiveAssignment,
        ):
            course = obj.assignment.course
        elif type(obj) == AdvancedProgrammingAssignment:
            course = obj.simple_programming_assignment.assignment.course
        elif type(obj) == Testcase:
            course = (
                obj.assignment.course
                if obj.assignment
                else obj.assignment_section.assignment.course
            )
        return course

    def has_permission(self, request, view):
        """
        Applicable at model level (GET, POST, PUT, PATCH, DELETE)
        """
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Applicable at model instance level (GET(one object), PUT, PATCH, DELETE)
        """
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            instructor_or_ta = is_instructor_or_ta(
                self._get_course_from_object(obj).id, request.user
            )
            if instructor_or_ta:
                return True
            return False


class IsInstructorOrTAOrReadOnly(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for: Course

    Allows:
        1. complete permissions to instructor/ta
        2. list/retrieve permissions to students/anonymous users
    """

    def has_permission(self, request, view):
        """
        Applicable at model level (GET, POST, PUT, PATCH, DELETE)
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Applicable at model instance level (GET(one object), PUT, PATCH, DELETE)
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            course_histories = CourseHistory.objects.filter(
                Q(course=obj) & (Q(role="I") | Q(role="T")) & Q(user=request.user)
            ).count()
            if course_histories:
                return True
            return False


class IsInstructorOrTAOrStudent(permissions.BasePermission):
    """Permission class for viewsets

    Applicable for: VideoHistory, SingleCorrectQuestionHistory,
                    MultipleCorrectQuestionHistory, FixedAnswerQuestionHistory,
                    DescriptiveQuestionhistory, CourseHistory, Crib, CribReply,
                    DiscussionThread, DiscussionComment, DiscussionReply,
                    SimpleProgrammingAssignmentHistory,
                    AdvancedProgrammingAssignmentHistory, TestcaseHistory,
                    ExamHistory, SubjectiveAssignmentHistory,
                    StudentProfile, InstructorProfile, Registration

    Allows:
        1. complete permissions to instructor/ta/students
    """

    def _get_user_from_object(self, obj):
        """get user from object instance

        Args:
            obj : Model objects (like VideoHistory)

        Returns:
            user: User model object
        """

        if type(obj) == Crib:
            user = obj.created_by
        if type(obj) in (DiscussionComment, DiscussionThread, DiscussionReply):
            user = obj.author
        if type(obj) in (
            SimpleProgrammingAssignmentHistory,
            SubjectiveAssignmentHistory,
        ):
            user = obj.assignment_history.user
        if type(obj) == AdvancedProgrammingAssignmentHistory:
            user = obj.simple_programming_assignment_history.assignment_history.user
        else:
            user = obj.user
        return user

    def has_permission(self, request, view):
        """
        Applicable at model level (GET, POST, PUT, PATCH, DELETE)
        """
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Applicable at model instance level (GET(one object), PUT, PATCH, DELETE)
        """
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True

            if self._get_user_from_object(obj).email == request.user.email:
                return True
            return False


class UserPermission(permissions.BasePermission):
    """Permision class for viewsets.

    Applicable for: User

    Allows:
        1. create permission to anonymous users
        2. list/retrieve permission to authenticated users
        3. update/partial_update/destroy to authenticated owners only
    """

    def has_permission(self, request, view):
        """
        Applicable at model level (GET, POST, PUT, PATCH, DELETE)
        """
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_authenticated:
                return True
        elif request.method == "POST":
            return True
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Applicable at model instance level (GET(one object), PUT, PATCH, DELETE)
        """
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_authenticated:
                return True
        if request.user.is_authenticated and obj.email == request.user.email:
            return True
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission class for viewsets

    Applicable for: SubscriptionHistory

    Allows:
        1. all permission to admin users
        2. list/retrieve to authenticated users
    """

    def has_permission(self, request, view):
        """
        Applicable at model level (GET, POST, PUT, PATCH, DELETE)
        """
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            elif request.user.is_admin:
                return True
        return False


class IsOwner(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for: Course

    Allows:
        1. complete permissions to instructor
    """

    def has_object_permission(self, request, view, obj):
        """
        Applicable at model instance level (GET(one object), PUT, PATCH, DELETE)
        """
        if request.user.is_authenticated and obj.owner == request.user:
            return True
        return False
