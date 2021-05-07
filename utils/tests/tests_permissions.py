from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory, APITestCase

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
from registration.models import SubscriptionHistory
from subjective_assignments.models import (
    SubjectiveAssignment,
    SubjectiveAssignmentHistory,
)
from utils.permissions import (
    IsAdmin,
    IsInstructorOrTA,
    IsInstructorOrTAOrReadOnly,
    IsInstructorOrTAOrStudent,
    IsOwner,
    UserPermission,
)
from video.models import QuizMarker, SectionMarker, Video, VideoHistory


User = get_user_model()


class PermissionHelperMixin:
    """Helper class for permision class tests."""

    def _permisison_helper(self, request, obj=None):
        """Helper method for `has_permission()` & `has_object_permission()` method.

        Args:
            request (Request): DRF `Request` object
            obj (Model, optional): `Model` instance (`Course`, 'Chapter` etc.).
                Defaults to None.
        """
        for user, assert_true in self.user_permissions:
            request.user = user
            if obj is None:
                permission = self.permission_class.has_permission(request, None)
            else:
                permission = self.permission_class.has_object_permission(
                    request, None, obj
                )
            if assert_true:
                self.assertTrue(permission)
            else:
                self.assertFalse(permission)


class IsInstructorOrTATest(APITestCase, PermissionHelperMixin):
    """Test for `IsInstructorOrTA` permission class."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "chapters.test.yaml",
        "sections.test.yaml",
        "videos.test.yaml",
        "documents.test.yaml",
        "quiz.test.yaml",
        "questionmodule.test.yaml",
        "sectionmarker.test.yaml",
        "quizmarker.test.yaml",
        "question.test.yaml",
        "singlecorrectquestion.test.yaml",
        "multiplecorrectquestion.test.yaml",
        "fixedanswerquestion.test.yaml",
        "descriptivequestion.test.yaml",
        "schedule.test.yaml",
        "pages.test.yaml",
        "announcement.test.yaml",
        "discussionforum.test.yaml",
        "assignment.test.yaml",
        "simpleprogrammingassignment.test.yaml",
        "advancedprogrammingassignment.test.yaml",
        "assignmentsection.test.yaml",
        "testcase.test.yaml",
        "exam.test.yaml",
        "subjectiveassignment.test.yaml",
        "notification.test.yaml",
        "email.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """Allows the creation of initial data at the class level."""
        cls.factory = APIRequestFactory()
        cls.permission_class = IsInstructorOrTA()

        cls.instructor = User.objects.get(id=1)
        cls.ta = User.objects.get(id=2)
        cls.student = User.objects.get(id=3)

        cls.chapter = Chapter.objects.get(id=1)
        cls.section = Section.objects.get(id=1)
        cls.video = Video.objects.get(id=1)
        cls.document = Document.objects.get(id=1)
        cls.quiz = Quiz.objects.get(id=1)
        cls.questionmodule = QuestionModule.objects.get(id=1)
        cls.sectionmarker = SectionMarker.objects.get(id=1)
        cls.quizmarker = QuizMarker.objects.get(id=1)
        cls.singlecorrectquestion = SingleCorrectQuestion.objects.get(id=1)
        cls.multiplecorrectquestion = MultipleCorrectQuestion.objects.get(id=3)
        cls.fixedanswerquestion = FixedAnswerQuestion.objects.get(id=5)
        cls.descriptivequestion = DescriptiveQuestion.objects.get(id=7)
        cls.schedule = Schedule.objects.get(id=1)
        cls.page = Page.objects.get(id=1)
        cls.announcement = Announcement.objects.get(id=1)
        cls.discussionforum = DiscussionForum.objects.get(id=1)
        cls.simpleprogrammingassignment = SimpleProgrammingAssignment.objects.get(id=1)
        cls.advancedprogrammingassignment = AdvancedProgrammingAssignment.objects.get(
            id=1
        )
        cls.assignmentsection = AssignmentSection.objects.get(id=1)
        cls.testcase = Testcase.objects.get(id=1)
        cls.exam = Exam.objects.get(id=1)
        cls.subjectiveassignment = SubjectiveAssignment.objects.get(id=1)
        cls.notification = Notification.objects.get(id=1)
        cls.email = Email.objects.get(id=1)

    def setUp(self):
        """Allows the creation of initial data at the method level."""
        self.user_permissions = [
            [self.instructor, True],
            [self.ta, True],
            [self.student, True],
            [AnonymousUser(), False],
        ]

    def _helper(self, request):
        self._permisison_helper(request)
        self.user_permissions[2][1] = False
        self._permisison_helper(request, self.chapter)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._permisison_helper(request)
        self._permisison_helper(request, self.chapter)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self._permisison_helper(request)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._helper(request)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._helper(request)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._helper(request)

    def test_get_course_from_object(self):
        """Test `_get_course_from_object()` method."""
        actual_course = self.permission_class._get_course_from_object(self.chapter)
        expected_course = self.chapter.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(self.section)
        expected_course = self.section.chapter.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(self.video)
        try:
            expected_course = self.video.chapter.course
        except Exception:
            expected_course = self.video.section.chapter.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(self.document)
        try:
            expected_course = self.document.chapter.course
        except Exception:
            expected_course = self.document.section.chapter.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(self.quiz)
        try:
            expected_course = self.quiz.chapter.course
        except Exception:
            expected_course = self.quiz.section.chapter.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(
            self.questionmodule
        )
        try:
            expected_course = self.questionmodule.quiz.chapter.course
        except Exception:
            expected_course = self.questionmodule.quiz.section.chapter.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(
            self.sectionmarker
        )
        try:
            expected_course = self.sectionmarker.video.chapter.course
        except Exception:
            expected_course = self.sectionmarker.video.section.chapter.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(self.quizmarker)
        try:
            expected_course = self.quizmarker.video.chapter.course
        except Exception:
            expected_course = self.quizmarker.video.section.chapter.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(
            self.singlecorrectquestion
        )
        try:
            expected_course = (
                self.singlecorrectquestion.question_module.quiz.chapter.course
            )
        except Exception:
            expected_course = (
                self.singlecorrectquestion.question_module.quiz.section.chapter.course
            )
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(
            self.multiplecorrectquestion
        )
        try:
            expected_course = (
                self.multiplecorrectquestion.question_module.quiz.chapter.course
            )
        except Exception:
            expected_course = (
                self.multiplecorrectquestion.question_module.quiz.section.chapter.course
            )
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(
            self.fixedanswerquestion
        )
        try:
            expected_course = (
                self.fixedanswerquestion.question_module.quiz.chapter.course
            )
        except Exception:
            expected_course = (
                self.fixedanswerquestion.question_module.quiz.section.chapter.course
            )
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(
            self.descriptivequestion
        )
        try:
            expected_course = (
                self.descriptivequestion.question_module.quiz.chapter.course
            )
        except Exception:
            expected_course = (
                self.descriptivequestion.question_module.quiz.section.chapter.course
            )
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(self.schedule)
        expected_course = self.schedule.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(self.page)
        expected_course = self.page.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(self.announcement)
        expected_course = self.announcement.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(
            self.discussionforum
        )
        expected_course = self.discussionforum.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(
            self.simpleprogrammingassignment
        )
        expected_course = self.simpleprogrammingassignment.assignment.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(
            self.advancedprogrammingassignment
        )
        advancedprogrammingassignment = self.advancedprogrammingassignment
        simpleprogrammingassignment = (
            advancedprogrammingassignment.simple_programming_assignment
        )
        expected_course = simpleprogrammingassignment.assignment.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(
            self.assignmentsection
        )
        expected_course = self.assignmentsection.assignment.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(self.testcase)
        expected_course = self.testcase.assignment.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(self.exam)
        expected_course = self.exam.assignment.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(
            self.subjectiveassignment
        )
        expected_course = self.subjectiveassignment.assignment.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(self.notification)
        expected_course = self.notification.course
        self.assertEqual(actual_course, expected_course)

        actual_course = self.permission_class._get_course_from_object(self.email)
        expected_course = self.email.course
        self.assertEqual(actual_course, expected_course)


class IsInstructorOrTAOrReadOnlyTest(APITestCase, PermissionHelperMixin):
    """Test for `IsInstructorOrTAOrReadOnly` permission class."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """Allows the creation of initial data at the class level."""
        cls.factory = APIRequestFactory()
        cls.permission_class = IsInstructorOrTAOrReadOnly()

        cls.instructor = User.objects.get(id=1)
        cls.ta = User.objects.get(id=2)
        cls.student = User.objects.get(id=3)

        cls.course = Course.objects.get(id=1)

    def setUp(self):
        """Allows the creation of initial data at the method level."""
        self.user_permissions = [
            [self.instructor, True],
            [self.ta, True],
            [self.student, True],
            [AnonymousUser(), True],
        ]

    def _helper(self, request):
        self.user_permissions[3][1] = False
        self._permisison_helper(request)
        self.user_permissions[2][1] = False
        self._permisison_helper(request, self.course)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._permisison_helper(request)
        self._permisison_helper(request, self.course)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self.user_permissions[3][1] = False
        self._permisison_helper(request)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._helper(request)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._helper(request)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._helper(request)


class IsInstructorOrTAOrStudentTest(APITestCase, PermissionHelperMixin):
    """Test for `IsInstructorOrTAOrStudent` permission class."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "chapters.test.yaml",
        "sections.test.yaml",
        "videos.test.yaml",
        "videohistories.test.yaml",
        "quiz.test.yaml",
        "questionmodule.test.yaml",
        "sectionmarker.test.yaml",
        "quizmarker.test.yaml",
        "question.test.yaml",
        "singlecorrectquestion.test.yaml",
        "multiplecorrectquestion.test.yaml",
        "fixedanswerquestion.test.yaml",
        "descriptivequestion.test.yaml",
        "questionhistory.test.yaml",
        "singlecorrectquestionhistory.test.yaml",
        "multiplecorrectquestionhistory.test.yaml",
        "fixedanswerquestionhistory.test.yaml",
        "descriptivequestionhistory.test.yaml",
        "discussionforum.test.yaml",
        "tags.test.yaml",
        "discussionthread.test.yaml",
        "discussioncomment.test.yaml",
        "discussionreply.test.yaml",
        "crib.test.yaml",
        "cribreply.test.yaml",
        "assignment.test.yaml",
        "simpleprogrammingassignment.test.yaml",
        "advancedprogrammingassignment.test.yaml",
        "assignmentsection.test.yaml",
        "testcase.test.yaml",
        "exam.test.yaml",
        "subjectiveassignment.test.yaml",
        "notification.test.yaml",
        "email.test.yaml",
        "assignmenthistory.test.yaml",
        "simpleprogrammingassignmenthistory.test.yaml",
        "advancedprogrammingassignmenthistory.test.yaml",
        "testcasehistory.test.yaml",
        "examhistory.test.yaml",
        "subjectiveassignmentteam.test.yaml",
        "subjectiveassignmenthistory.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """Allows the creation of initial data at the class level."""
        cls.factory = APIRequestFactory()
        cls.permission_class = IsInstructorOrTAOrStudent()

        cls.instructor = User.objects.get(id=1)
        cls.ta = User.objects.get(id=2)
        cls.student = User.objects.get(id=3)

        cls.course_history_inst = CourseHistory.objects.get(id=1)
        cls.course_history_ta = CourseHistory.objects.get(id=2)
        cls.course_history_stud = CourseHistory.objects.get(id=3)
        cls.video_history_inst = VideoHistory.objects.get(id=1)
        cls.single_correct_question_history_inst = (
            SingleCorrectQuestionHistory.objects.get(id=1)
        )
        cls.multiple_correct_question_history_inst = (
            MulitpleCorrectQuestionHistory.objects.get(id=4)
        )
        cls.fixed_answer_question_history_inst = (
            FixedCorrectQuestionHistory.objects.get(id=7)
        )
        cls.descriptive_question_history_inst = DescriptiveQuestionHistory.objects.get(
            id=10
        )
        cls.discussion_thread = DiscussionThread.objects.get(id=1)
        cls.discussion_comment = DiscussionComment.objects.get(id=1)
        cls.discussion_reply = DiscussionReply.objects.get(id=1)
        cls.crib = Crib.objects.get(id=1)
        cls.crib_reply = CribReply.objects.get(id=1)
        cls.simple_programming_assignment_history = (
            SimpleProgrammingAssignmentHistory.objects.get(id=1)
        )
        cls.advanced_programming_assignment_history = (
            AdvancedProgrammingAssignmentHistory.objects.get(id=1)
        )
        cls.testcase_history = TestcaseHistory.objects.get(id=1)
        cls.exam_history = ExamHistory.objects.get(id=1)
        cls.subjective_assignment_history = SubjectiveAssignmentHistory.objects.get(
            id=1
        )

    def setUp(self):
        """Allows the creation of initial data at the method level."""
        self.user_permissions = [
            [self.instructor, True],
            [self.ta, True],
            [self.student, True],
            [AnonymousUser(), False],
        ]

    def _helper(self, request):
        self._permisison_helper(request)
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self._permisison_helper(request, self.course_history_inst)
        self.user_permissions[0][1] = False
        self.user_permissions[1][1] = True
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self._permisison_helper(request, self.course_history_ta)
        self.user_permissions[0][1] = False
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = True
        self.user_permissions[3][1] = False
        self._permisison_helper(request, self.course_history_stud)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._permisison_helper(request)
        self._permisison_helper(request, self.course_history_inst)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self._permisison_helper(request)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._helper(request)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._helper(request)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._helper(request)

    def test_get_course_and_user_from_object(self):
        """Test `_get_course_and_user_from_object()` method."""
        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.course_history_inst
        )
        expected_user = self.course_history_inst.user
        expected_course = self.course_history_inst.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.video_history_inst
        )
        expected_user = self.video_history_inst.user
        try:
            expected_course = self.video_history_inst.video.chapter.course
        except Exception:
            expected_course = self.video_history_inst.video.section.chapter.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.single_correct_question_history_inst
        )
        expected_user = self.single_correct_question_history_inst.user
        question = self.single_correct_question_history_inst.question
        try:
            expected_course = question.question_module.quiz.chapter.course
        except Exception:
            expected_course = question.question_module.quiz.section.chapter.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.multiple_correct_question_history_inst
        )
        expected_user = self.multiple_correct_question_history_inst.user
        question = self.multiple_correct_question_history_inst.question
        try:
            expected_course = question.question_module.quiz.chapter.course
        except Exception:
            expected_course = question.question_module.quiz.section.chapter.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.fixed_answer_question_history_inst
        )
        expected_user = self.fixed_answer_question_history_inst.user
        question = self.fixed_answer_question_history_inst.question
        try:
            expected_course = question.question_module.quiz.chapter.course
        except Exception:
            expected_course = question.question_module.quiz.section.chapter.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.descriptive_question_history_inst
        )
        expected_user = self.descriptive_question_history_inst.user
        question = self.descriptive_question_history_inst.question
        try:
            expected_course = question.question_module.quiz.chapter.course
        except Exception:
            expected_course = question.question_module.quiz.section.chapter.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.discussion_thread
        )
        expected_user = self.discussion_thread.author
        expected_course = self.discussion_thread.discussion_forum.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.discussion_comment
        )
        expected_user = self.discussion_comment.discussion_thread.author
        expected_course = (
            self.discussion_comment.discussion_thread.discussion_forum.course
        )
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.discussion_reply
        )
        expected_user = (
            self.discussion_reply.discussion_comment.discussion_thread.author
        )
        discussion_thread = self.discussion_reply.discussion_comment.discussion_thread
        expected_course = discussion_thread.discussion_forum.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(self.crib)
        expected_user = self.crib.created_by
        expected_course = self.crib.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(self.crib_reply)
        expected_user = self.crib_reply.user
        expected_course = self.crib_reply.crib.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.simple_programming_assignment_history
        )
        expected_user = (
            self.simple_programming_assignment_history.assignment_history.user
        )
        assign_hist = self.simple_programming_assignment_history.assignment_history
        expected_course = assign_hist.assignment.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.advanced_programming_assignment_history
        )
        adv_prog_assign_hist = self.advanced_programming_assignment_history
        sim_prog_assign_hist = (
            adv_prog_assign_hist.simple_programming_assignment_history
        )
        expected_user = sim_prog_assign_hist.assignment_history.user
        expected_course = sim_prog_assign_hist.assignment_history.assignment.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.testcase_history
        )
        expected_user = self.testcase_history.user
        try:
            expected_course = self.testcase_history.testcase.assignment.course
        except Exception:
            expected_course = (
                self.testcase_history.testcase.assignment_section.assignment.course
            )
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(self.exam_history)
        expected_user = self.exam_history.user
        expected_course = self.exam_history.exam.assignment.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)

        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.subjective_assignment_history
        )
        expected_user = self.subjective_assignment_history.assignment_history.user
        expected_course = (
            self.subjective_assignment_history.assignment_history.assignment.course
        )
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)


class UserPermissionTest(APITestCase, PermissionHelperMixin):
    """Test for `UserPermission` permission class."""

    fixtures = [
        "users.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """Allows the creation of initial data at the class level."""
        cls.factory = APIRequestFactory()
        cls.permission_class = UserPermission()

        cls.admin = User.objects.create_superuser(
            email="admin@bodhitree.com", password="admin"
        )
        cls.instructor = User.objects.get(id=1)
        cls.ta = User.objects.get(id=2)
        cls.student = User.objects.get(id=3)

    def setUp(self):
        """Allows the creation of initial data at the method level."""
        self.user_permissions = [
            [self.admin, True],
            [self.instructor, True],
            [self.ta, True],
            [self.student, True],
            [AnonymousUser(), False],
        ]

    def _helper(self, request):
        self._permisison_helper(request)
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = True
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self.user_permissions[4][1] = False
        self._permisison_helper(request, self.instructor)
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = True
        self.user_permissions[3][1] = False
        self.user_permissions[4][1] = False
        self._permisison_helper(request, self.ta)
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = True
        self.user_permissions[4][1] = False
        self._permisison_helper(request, self.student)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._helper(request)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self.user_permissions[4][1] = True
        self._permisison_helper(request)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._helper(request)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._helper(request)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._helper(request)


class IsAdminTest(APITestCase, PermissionHelperMixin):
    """Test for `IsAdmin` permission class."""

    fixtures = [
        "users.test.yaml",
        "plans.test.yaml",
        "subscriptions.test.yaml",
        "subscriptionhistories.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """Allows the creation of initial data at the class level."""
        cls.factory = APIRequestFactory()
        cls.permission_class = IsAdmin()

        cls.admin = User.objects.create_superuser(
            email="admin@bodhitree.com", password="admin"
        )
        cls.instructor = User.objects.get(id=1)
        cls.ta = User.objects.get(id=2)
        cls.student = User.objects.get(id=3)

        cls.subscription_history = SubscriptionHistory.objects.get(id=1)

    def setUp(self):
        """Allows the creation of initial data at the method level."""
        self.user_permissions = [
            [self.admin, True],
            [self.instructor, True],
            [self.ta, True],
            [self.student, True],
            [AnonymousUser(), False],
        ]

    def _helper(self, request):
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self.user_permissions[4][1] = False
        self._permisison_helper(request)
        self._permisison_helper(request, self.subscription_history)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._permisison_helper(request)
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = True
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self.user_permissions[4][1] = False
        self._permisison_helper(request, self.subscription_history)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self.user_permissions[4][1] = False
        self._permisison_helper(request)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._helper(request)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._helper(request)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._helper(request)


class IsOwnerTest(APITestCase, PermissionHelperMixin):
    """Test for `IsOwner` permission class."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """Allows the creation of initial data at the class level."""
        cls.factory = APIRequestFactory()
        cls.permission_class = IsOwner()

        cls.instructor = User.objects.get(id=1)
        cls.ta = User.objects.get(id=2)
        cls.student = User.objects.get(id=3)

        cls.course = Course.objects.get(id=1)

    def setUp(self):
        """Allows the creation of initial data at the method level."""
        self.user_permissions = [
            [self.instructor, True],
            [self.ta, True],
            [self.student, True],
            [AnonymousUser(), False],
        ]

    def _helper(self, request):
        self._permisison_helper(request)
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self._permisison_helper(request, self.course)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._helper(request)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self._permisison_helper(request)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._helper(request)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._helper(request)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._helper(request)

    def test_get_user_from_object(self):
        """Test `_get_user_from_object()` method."""
        for obj in [self.course]:
            actual_user = self.permission_class._get_user_from_object(obj)
            expected_user = obj.owner
            self.assertEqual(actual_user, expected_user)
