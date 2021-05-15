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
from cribs.models import Crib, CribReply
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
    ExamHistory,
    SimpleProgrammingAssignment,
    SimpleProgrammingAssignmentHistory,
    Testcase,
    TestcaseHistory,
)
from quiz.models import (
    DescriptiveQuestion,
    DescriptiveQuestionHistory,
    FixedAnswerQuestion,
    FixedCorrectQuestionHistory,
    MulitpleCorrectQuestionHistory,
    MultipleCorrectQuestion,
    QuestionModule,
    Quiz,
    SingleCorrectQuestion,
    SingleCorrectQuestionHistory,
)
from subjective_assignments.models import (
    SubjectiveAssignment,
    SubjectiveAssignmentHistory,
)
from utils.utils import check_course_registration, check_is_instructor_or_ta
from video.models import QuizMarker, SectionMarker, Video, VideoHistory


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
        1. `GET (list)` permission to instructor/ta/student
            (If above is not desirable, then one way is: check `is_registered()`
                in api.py)
        2  `POST` permission to instructor/ta/student
            (If above is not desirable, then one way is: check `is_instructor_or_ta()`
                in api.py)
        3. `GET (retrieve)` permission to registered instructor/ta/student
        4. `PUT` permision to registered instructor/ta
        5. `PATCH` permision to registered instructor/ta
        6. `DELETE` permision to registered instructor/ta
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
            AdvancedProgrammingAssignment,
            SubjectiveAssignment,
        ):
            course = obj.course
        elif type(obj) in (Exam, AssignmentSection):
            course = obj.assignment.course
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
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Applicable at model instance level (GET(retrieve), PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`ChapterViewSet`, `VideoViewSet` etc.)
            obj (Model): `Model` object (`Chapter`, `Video` etc.)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        user = request.user
        if user and user.is_authenticated:
            course_id = self._get_course_from_object(obj).id

            if request.method in permissions.SAFE_METHODS:
                return check_course_registration(course_id, user)
            return check_is_instructor_or_ta(course_id, user)
        return False


class StrictIsInstructorOrTA(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for:
        1. Crib
        2. CribReply

    Allows:
        1. All permissions to instructor/ta
        2. No permissions to student (GET(list) and POST are exceptions)
        3. No permissions to anonymous user
    """

    def has_permission(self, request, view):
        """Applicable at model level (GET, POST, PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`CribViewSet`)

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
        if type(obj) == Crib:
            course_id = obj.course_id
        elif type(obj) == CribReply:
            course_id = obj.crib.course_id
        if request.user.is_authenticated:
            instructor_or_ta = check_is_instructor_or_ta(course_id, request.user)
            if instructor_or_ta:
                return True
        return False


class IsInstructorOrTAOrReadOnly(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for: Course

    Allows:
        1. `GET (list)` permission to instructor/ta/student/anonymous
        2  `POST` permission to instructor/ta/student
            (check `is_course_limit_reached()` in api.py)
        3. `GET (retrieve)` permission to instructor/ta/student/anonymous
        4. `PUT` permision to registered instructor/ta
            (check `has_valid_subscription()` in api.py)
        5. `PATCH` permision to registered instructor/ta
            (check `has_valid_subscription()` in api.py)
        6. `DELETE` permision to registered instructor/ta
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

        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Applicable at model instance level (GET(retrieve), PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`CourseViewSet`)
            obj (Model): `Model` object (`Course`)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        return bool(
            user and user.is_authenticated and check_is_instructor_or_ta(obj.id, user)
        )


class IsInstructorOrTAOrStudent(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for:
        1. CourseHistory, VideoHistory
        2. SingleCorrectQuestionHistory, MultipleCorrectQuestionHistory,
           FixedAnswerQuestionHistory, DescriptiveQuestionhistory
        3. DiscussionThread, DiscussionComment, DiscussionReply
        4. Crib, CribReply
        5. SimpleProgrammingAssignmentHistory, AdvancedProgrammingAssignmentHistory
        6. TestcaseHistory, ExamHistory
        7. SubjectiveAssignmentHistory

    Allows:
        1. `GET (list)` permission to instructor/ta/student
            (If above is not desirable, then one way is: check `is_registered()`
                in api.py)
        2  `POST` permission to instructor/ta/student
            (If above is not desirable, then one way is: check `is_registered()`
                in api.py)
        3. `GET (retrieve)` permission to registered instructor/ta/student
        4. `PUT` permision to owner
        5. `PATCH` permision to owner
        6. `DELETE` permision to owner
    """

    def _get_course_and_user_from_object(self, obj):
        """Get course and user using obj.

        Args:
            obj (Model): `Model` object (`CourseHistory`, `DiscussionThread` etc.)

        Returns:
            course (Course): `Course` model object
            user (User): `User` model object
        """
        if type(obj) == CourseHistory:
            course = obj.course
            user = obj.user
        elif type(obj) == VideoHistory:
            course = (
                obj.video.chapter.course
                if obj.video.chapter
                else obj.video.section.chapter.course
            )
            user = obj.user
        elif type(obj) in (
            SingleCorrectQuestionHistory,
            MulitpleCorrectQuestionHistory,
            FixedCorrectQuestionHistory,
            DescriptiveQuestionHistory,
        ):
            course = (
                obj.question.question_module.quiz.chapter.course
                if obj.question.question_module.quiz.chapter
                else obj.question.question_module.quiz.section.chapter.course
            )
            user = obj.user
        elif type(obj) == DiscussionThread:
            course = obj.discussion_forum.course
            user = obj.author
        elif type(obj) == DiscussionComment:
            course = obj.discussion_thread.discussion_forum.course
            user = obj.author
        elif type(obj) == DiscussionReply:
            course = obj.discussion_comment.discussion_thread.discussion_forum.course
            user = obj.author
        elif type(obj) == Crib:
            course = obj.course
            user = obj.created_by
        elif type(obj) == CribReply:
            course = obj.crib.course
            user = obj.user
        elif type(obj) in (
            SimpleProgrammingAssignmentHistory,
            AdvancedProgrammingAssignmentHistory,
        ):
            course = obj.simple_prog_assignment.course
            user = obj.user
        elif type(obj) in (SubjectiveAssignmentHistory,):
            course = obj.assignment.course
            user = obj.user
        elif type(obj) == ExamHistory:
            course = obj.exam.assignment.course
            user = obj.user
        elif type(obj) == TestcaseHistory:
            course = (
                obj.testcase.assignment.course
                if obj.testcase.assignment
                else obj.testcase.assignment_section.assignment.course
            )
            user = obj.user
        return (course, user)

    def has_permission(self, request, view):
        """Applicable at model level (GET, POST, PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`DiscussionThreadViewSet` etc.)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Applicable at model instance level (GET(retrieve), PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`DiscussionThreadViewSet` etc.)
            obj (Model): `Model` object (`DiscussionThread` etc.)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        user = request.user
        if user and user.is_authenticated:
            course_from_obj, user_from_obj = self._get_course_and_user_from_object(obj)
            if request.method in permissions.SAFE_METHODS:
                return check_course_registration(course_from_obj.id, user)
            return (
                check_course_registration(course_from_obj.id, user)
                and user_from_obj == user
            )
        return False


class UserPermission(permissions.BasePermission):
    """Permision class for viewsets.

    Applicable for: User

    Allows:
        1. `GET (list)` permission to any authenticated user
            (If above is not desirable, then one way is: don't provide `list()` method)
        2  `POST` permisison to authenticated/not_authenticated user
        3. `GET (retrieve)` permission to owner or admin user
        4. `PUT` permision to owner or admin user
        5. `PATCH` permision to owner or admin user
        6. `DELETE` permision to owner  or admin user
    """

    def has_permission(self, request, view):
        """Applicable at model level (GET, POST, PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`UserViewSet`)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        if request.method == "POST":
            return True

        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Applicable at model instance level (GET(retrieve), PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`UserViewSet`)
            obj (Model): `Model` object (`User`)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        user = request.user
        return bool(user and user.is_authenticated and (obj == user or user.is_admin))


class IsAdmin(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for: SubscriptionHistory

    Allows:
        1. `GET (list)` permission to any authenticated user
            (If above is not desirable, then one way is: don't provide `list()` method)
        2  `POST` permisison to any admin user
        3. `GET (retrieve)` permission to owner or admin user
        4. `PUT` permision to admin user
        5. `PATCH` permision to admin user
        6. `DELETE` permision to admin user
    """

    def has_permission(self, request, view):
        """Applicable at model level (GET, POST, PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`SubscriptionHistoryViewSet`)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        user = request.user
        if user and user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            elif user.is_admin:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        """Applicable at model instance level (GET(retrieve), PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`SubscriptionHistoryViewSet`)
            obj (Model): `Model` object (`SubscriptionHistory`)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        user = request.user
        if user and user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return bool(obj.user == user or user.is_admin)
            elif user.is_admin:
                return True
        return False


class IsOwner(permissions.BasePermission):
    """Permission class for viewsets.

    Applicable for:
        1. Course, CourseHistory
        2. Crib, CribReply

    Allows:
        1. `GET (list)` permission to any authenticated user
            (If above is not desirable, then one way is: don't provide `list()` method)
        2  `POST` permisison to any authenticated user
            (If above is not desirable, then one way is: don't provide `create()`
                method)
        3. `GET (retrieve)` permission to owner
        4. `PUT` permision to owner
        5. `PATCH` permision to owner
        6. `DELETE` permision to owner
    """

    def _get_user_from_object(self, obj):
        """Get user using obj.

        Args:
            obj (Model): `Model` object (`Course`, `Crib` etc.)

        Returns:
            user (User): `User` model object
        """
        if type(obj) == Course:
            user = obj.owner
        elif type(obj) == CourseHistory:
            user = obj.user
        elif type(obj) == Crib:
            user = obj.created_by
        elif type(obj) == CribReply:
            user = obj.user
        return user

    def has_permission(self, request, view):
        """Applicable at model level (GET, POST, PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`CourseViewSet` etc.)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Applicable at model instance level (GET(retrieve), PUT, PATCH, DELETE).

        Args:
            request (Request): DRF `Request` object
            view (ViewSet): `ViewSet` object (`CourseViewSet` etc.)
            obj (Model): `Model` object (`Course` etc.)

        Returns:
            A bool value denoting whether method (`GET`, `POST` etc.) is allowed or not.
        """
        user = request.user
        return bool(
            user and user.is_authenticated and self._get_user_from_object(obj) == user
        )
