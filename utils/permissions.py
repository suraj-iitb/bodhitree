from rest_framework import permissions

from course.models import (
    Announcement,
    Chapter,
    Course,
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
from utils.utils import check_is_instructor_or_ta
from video.models import QuizMarker, SectionMarker, Video


class IsInstructorOrTA(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for:
        1. Chapter, Section, Video, Document
        2. Quiz, QuestionModule, SectionMarker, QuizMarker
        3. SingleCorrectQuestion, MultipleCorrectQuestion, FixedAnswerQuestion,
           DescriptiveQuestion
        4. Schedule, Page, Announcement, DiscussionForum
        5. SimpleProgrammingAssignment, AdvancedProgrammingAssignment
        6. AssignmentSection, Testcase, Exam
        7. SubjectiveAssignment
        8. Notification, Email

    Allows:
        1. All permissions to instructor/ta
        2. Only `GET` permisision to student (`POST` is an exception)
        3. No permissions to anonymous user
    """

    def _get_course_from_object(self, obj):
        """Get course using obj.

        Args:
            obj (Model): `Model` object (`Chapter`, `Quiz` etc.)

        Returns:
            course (Course): `Course` model object
        """
        if type(obj) in (
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
            Video,
            Document,
            Quiz,
        ):
            course = obj.chapter.course if obj.chapter else obj.section.chapter.course
        elif type(obj) in (
            SectionMarker,
            QuizMarker,
        ):
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
        """Applicable at model level (GET, POST, PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`ChapterViewSet`, `VideoViewSet` etc.)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Applicable at model instance level (GET(one object), PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`ChapterViewSet`, `QuizViewSet` etc.)
            obj (Model): `Model` object (`Chapter`, `Quiz` etc.)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            instructor_or_ta = check_is_instructor_or_ta(
                self._get_course_from_object(obj).id, request.user
            )
            if instructor_or_ta:
                return True
        return False


class IsInstructorOrTAOrReadOnly(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for: Course

    Allows:
        1. All permissions to instructor/ta.
        2. Only `GET` permisision to student (`POST` is an exception)
        3. Only `GET` permisision to anonymous user
    """

    def has_permission(self, request, view):
        """Applicable at model level (GET, POST, PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`CourseViewSet`)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Applicable at model instance level (GET(one object), PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`CourseViewSet`)
            obj (Model): `Model` object (`Course`)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            instructor_or_ta = check_is_instructor_or_ta(obj.id, request.user)
            if instructor_or_ta:
                return True
        return False


class IsInstructorOrTAOrStudent(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for:
        1. CourseHistory, VideoHistory
        2. Registration
        3. SingleCorrectQuestionHistory, MultipleCorrectQuestionHistory,
           FixedAnswerQuestionHistory, DescriptiveQuestionhistory
        4. DiscussionThread, DiscussionComment, DiscussionReply
        5. Crib, CribReply
        6. SimpleProgrammingAssignmentHistory, AdvancedProgrammingAssignmentHistory
        7. TestcaseHistory, ExamHistory
        8. SubjectiveAssignmentHistory

    Allows:
        1. All permissions to instructor/ta/student
        2. No permissions to anonymous user
    """

    def _get_user_from_object(self, obj):
        """Get user using obj.

        Args:
            obj (Model): `Model` object (`CourseHistory`, `DiscussionThread` etc.)

        Returns:
            user (User): `User` model object
        """
        if type(obj) in (
            DiscussionThread,
            DiscussionComment,
            DiscussionReply,
        ):
            user = obj.author
        elif type(obj) == Crib:
            user = obj.created_by
        elif type(obj) in (
            SimpleProgrammingAssignmentHistory,
            SubjectiveAssignmentHistory,
        ):
            user = obj.assignment_history.user
        elif type(obj) == AdvancedProgrammingAssignmentHistory:
            user = obj.simple_programming_assignment_history.assignment_history.user
        else:
            user = obj.user
        return user

    def has_permission(self, request, view):
        """Applicable at model level (GET, POST, PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`DiscussionThreadViewSet` etc.)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Applicable at model instance level (GET(one object), PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`DiscussionThreadViewSet` etc.)
            obj (Model): `Model` object (`DiscussionThread`, `Crib` etc.)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True

            if self._get_user_from_object(obj) == request.user:
                return True
            return False


class UserPermission(permissions.BasePermission):
    """Permision class for viewsets.

    Applicable for: User

    Allows:
        1. `POST` permission to anonymous user
        2. `GET` permission to authenticated user
        3. `PUT/PATCH/DELETE` permission to authenticated owner
    """

    def has_permission(self, request, view):
        """Applicable at model level (GET, POST, PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`UserViewSet`)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_authenticated:
                return True
        elif request.method == "POST":
            return True
        elif request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Applicable at model instance level (GET(one object), PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`UserViewSet`)
            obj (Model): `Model` object (`User`)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_authenticated:
                return True
        elif request.user.is_authenticated and obj == request.user:
            return True
        return False


class IsAdmin(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for: SubscriptionHistory

    Allows:
        1. All permissions to admin users
        2. Only `GET` permisision to instructor/ta/student
        3. No permissions to anonymous user
    """

    def has_permission(self, request, view):
        """Applicable at model level (GET, POST, PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`SubscriptionHistoryViewSet`)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            elif request.user.is_admin:
                return True
        return False


class IsOwner(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for: Course, CourseHistory

    Allows:
        1. All permissions to owner
        2. Only `GET` permisision to instructor/ta/student
        3. No permissions to anonymous user
    """

    def _get_user_from_object(self, obj):
        """Get user using obj.

        Args:
            obj (Model): `Model` object (`Course`, `CourseHistory`)

        Returns:
            user (User): `User` model object
        """
        if type(obj) == Course:
            user = obj.owner
        elif type(obj) == CourseHistory:
            user = obj.user
        return user

    def has_permission(self, request, view):
        """Applicable at model level (GET, POST, PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`Course`, `CourseViewSet`)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Applicable at model instance level (GET(one object), PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`Course`, `CourseViewSet`)
            obj (Model): `Model` object (`Course`, `CourseHistory`)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            elif self._get_user_from_object(obj) == request.user:
                return True
        return False
