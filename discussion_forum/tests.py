from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from utils import credentials

from .models import DiscussionThread


ins_cred = credentials.TEST_INSTRUCTOR_CREDENTIALS
ta_cred = credentials.TEST_TA_CREDENTIALS
stu_cred = credentials.TEST_STUDENT_CREDENTIALS


class DiscussionThreadViewSetTest(APITestCase):
    """Test for `DiscussionThreadViewSet`."""

    fixtures = [
        "users.test.yaml",
        "colleges.test.yaml",
        "departments.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "chapters.test.yaml",
        "sections.test.yaml",
        "documents.test.yaml",
        "videos.test.yaml",
        "discussionforum.tests.yaml",
        "tags.test.yaml",
        "discussionthread.tests.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _list_discussion_threads_helper(self, discussion_forum_id, status_code):
        """Helper function for `test_list_discussion_threads()`.

        Args:
            discussion_forum_id (int): Discussion forum id
            status_code (int): Expected status code of the API call
        """
        url = reverse(
            "discussion_forum:discussionthread-list-discussion-threads",
            args=[discussion_forum_id],
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(
                len(response.data["results"]),
                DiscussionThread.objects.filter(
                    discussion_forum_id=discussion_forum_id
                ).count(),
            )

    def test_list_discussion_threads(self):
        """Test: list all discussion_threads."""
        discussion_forum_id = 1

        # List by instructor
        self.login(**ins_cred)
        self._list_discussion_threads_helper(discussion_forum_id, status.HTTP_200_OK)
        self.logout()

        # List by ta
        self.login(**ta_cred)
        self._list_discussion_threads_helper(discussion_forum_id, status.HTTP_200_OK)
        self.logout()

        # List by student
        self.login(**stu_cred)
        self._list_discussion_threads_helper(discussion_forum_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTAOrStudent`
        self._list_discussion_threads_helper(
            discussion_forum_id, status.HTTP_401_UNAUTHORIZED
        )

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        discussion_forum_id = 2
        self.login(**stu_cred)
        self._list_discussion_threads_helper(
            discussion_forum_id, status.HTTP_403_FORBIDDEN
        )
        self.logout()

    def _retrieve_discussion_thread_helper(self, discussion_thread_id, status_code):
        """Helper function for `test_retrieve_discussion_thread()`.

        Args:
            discussion_thread_id (int): Discussion thread id
            status_code (int): Expected status code of the API call
        """
        url = reverse(
            "discussion_forum:discussionthread-retrieve-discussion-thread",
            args=[discussion_thread_id],
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], discussion_thread_id)

    def test_retrieve_discussion_thread(self):
        """Test: retrieve discussion_thread."""
        discussion_thread_id = 1

        # Retrieve by instructor
        self.login(**ins_cred)
        self._retrieve_discussion_thread_helper(
            discussion_thread_id, status.HTTP_200_OK
        )
        self.logout()

        # Retrieve by ta
        self.login(**ta_cred)
        self._retrieve_discussion_thread_helper(
            discussion_thread_id, status.HTTP_200_OK
        )
        self.logout()

        # Retrieve by student
        self.login(**stu_cred)
        self._retrieve_discussion_thread_helper(
            discussion_thread_id, status.HTTP_200_OK
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTAOrStudent` permission class
        self._retrieve_discussion_thread_helper(
            discussion_thread_id, status.HTTP_401_UNAUTHORIZED
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTAOrStudent` permission class
        discussion_thread_id = 4
        self.login(**stu_cred)
        self._retrieve_discussion_thread_helper(
            discussion_thread_id, status.HTTP_403_FORBIDDEN
        )
        self.logout()

    def _create_discussion_thread_helper(
        self, discussion_forum_id, title, status_code, author_id, author_category
    ):
        """Helper function for `test_create_discussion_thread()`.

        Args:
            discussion_forum_id (int): Discussion forum id
            title (str): Title of the discussion thread
            status_code (int): Expected status code of the API call
            author_id (int): User id
            author_category (str): User category(inst/stud/ta)
        """
        data = {
            "discussion_forum": discussion_forum_id,
            "title": title,
            "mark_as_important": True,
            "author": author_id,
            "author_category": author_category,
            "description": "Description of discussion thread",
            "pinned": True,
            "anonymous_to_student": True,
            "upvote": 0,
            "downvote": 0,
        }
        url = reverse("discussion_forum:discussionthread-create-discussion-thread")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            for field in [
                "created_on",
                "modified_on",
                "id",
                "tag",
            ]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def test_create_discussion_thread(self):
        """Test: create a discussion thread."""
        discussion_forum_id = 1

        # Created by instructor
        self.login(**ins_cred)
        self._create_discussion_thread_helper(
            discussion_forum_id, "DiscussionThread 1", status.HTTP_201_CREATED, 1, "I"
        )
        self.logout()

        # Created by ta
        self.login(**ta_cred)
        self._create_discussion_thread_helper(
            discussion_forum_id, "DiscussionThread 2", status.HTTP_201_CREATED, 2, "T"
        )
        self.logout()

        # Created by student
        self.login(**stu_cred)
        self._create_discussion_thread_helper(
            discussion_forum_id, "DiscussionThread 3", status.HTTP_201_CREATED, 3, "S"
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to `is_valid()` method of the serailizer
        self.login(**stu_cred)
        self._create_discussion_thread_helper(
            discussion_forum_id, "", status.HTTP_400_BAD_REQUEST, 3, "S"
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOeTAOrStudent` permission class
        self._create_discussion_thread_helper(
            discussion_forum_id,
            "DiscussionThread 5",
            status.HTTP_401_UNAUTHORIZED,
            3,
            "S",
        )

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        discussion_forum_id = 2
        self.login(**stu_cred)
        self._create_discussion_thread_helper(
            discussion_forum_id, "DiscussionThread 6", status.HTTP_403_FORBIDDEN, 3, "S"
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to discussion forum does not exist
        discussion_forum_id = 3
        self.login(**stu_cred)
        self._create_discussion_thread_helper(
            discussion_forum_id, "DiscussionThread 6", status.HTTP_404_NOT_FOUND, 3, "S"
        )
        self.logout()

    def _update_discussion_thread_helper(
        self,
        discussion_forum_id,
        title,
        status_code,
        author_id,
        author_category,
        method,
    ):
        """
        Helper function for `test_partial_update_discussion_thread()`
            and `test_update_discussion_thread()`.

        Args:
            discussion_forum_id (int): Discussion forum id
            title (str): Title of the discussion thread
            status_code (int): Expected status code of the API call
            author_id (int): User id
            author_category (str): User category(inst/stud/ta)
            method (str): HTTP method ("PUT or "PATCH")
        """
        discussion_thread = DiscussionThread(
            title="DiscussionThread 4",
            discussion_forum_id=discussion_forum_id,
            author_id=author_id,
            author_category=author_category,
        )
        discussion_thread.save()
        data = {
            "discussion_forum": discussion_forum_id,
            "title": title,
            "mark_as_important": True,
            "author": author_id,
            "author_category": author_category,
            "description": "Description of discussion thread",
            "pinned": True,
            "anonymous_to_student": True,
            "upvote": 0,
            "downvote": 0,
        }
        url = reverse(
            ("discussion_forum:discussionthread-update-discussion-thread"),
            args=[discussion_thread.id],
        )
        if method == "PUT":
            response = self.client.put(url, data)
        else:
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            for field in [
                "created_on",
                "modified_on",
                "id",
                "tag",
            ]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def _put_or_patch(self, method):
        """Test: update discussion thread functionality."""
        discussion_forum_id = 1

        # Update by instructor
        self.login(**ins_cred)
        self._update_discussion_thread_helper(
            discussion_forum_id,
            "DiscussionThread 5",
            status.HTTP_200_OK,
            1,
            "I",
            method,
        )
        self.logout()

        # Update by ta
        self.login(**ta_cred)
        self._update_discussion_thread_helper(
            discussion_forum_id,
            "DiscussionThread 6",
            status.HTTP_200_OK,
            2,
            "T",
            method,
        )
        self.logout()

        # Update by student
        self.login(**stu_cred)
        self._update_discussion_thread_helper(
            discussion_forum_id,
            "DiscussionThread 7",
            status.HTTP_200_OK,
            3,
            "S",
            method,
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to `is_valid()` method of the serializer
        self.login(**stu_cred)
        self._update_discussion_thread_helper(
            discussion_forum_id, "", status.HTTP_400_BAD_REQUEST, 3, "S", method
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOeTAOrStudent` permission class
        self._update_discussion_thread_helper(
            discussion_forum_id,
            "DiscussionThread 5",
            status.HTTP_401_UNAUTHORIZED,
            3,
            "S",
            method,
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTAOrStudent` permission class
        self.login(**stu_cred)
        self._update_discussion_thread_helper(
            1, "DiscussionThread 6", status.HTTP_403_FORBIDDEN, 2, "S", method
        )
        self.logout()

    def test_update_discussion_thread(self):
        """Test: update the discussion thread."""
        self._put_or_patch("PUT")

    def test_partial_update_discussion_thread(self):
        """Test: partial update the discussion thread."""
        self._put_or_patch("PATCH")


# class DiscussionCommentViewSetTest(APITestCase):
#     """Test for DiscussionCommentViewSet."""

#     fixtures = [
#         "users.test.yaml",
#         "colleges.test.yaml",
#         "departments.test.yaml",
#         "chapters.test.yaml",
#         "sections.test.yaml",
#         "documents.test.yaml",
#         "courses.test.yaml",
#         "coursehistories.test.yaml",
#         "videos.test.yaml",
#         "discussionforum.tests.yaml",
#         "tags.test.yaml",
#         "discussionthread.tests.yaml",
#         "discussioncomment.test.yaml",
#     ]

#     def _list_discussion_comments_helper(self):
#         """Helper function to test list discussion comments functionality."""
#         discussion_thread_id = 1
#         url = reverse(
#             "discussion_forum:discussioncomment-list-discussion-comments",
#             args=[discussion_thread_id],
#         )
#         response = self.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), DiscussionComment.objects.all().count())

#     def test_list_discussion_comments(self):
#         """Test to check: list all discussion_comments."""
#         self.login(**ins_cred)
#         self._list_discussion_comments_helper()
#         self.logout()
#         self.login(**ta_cred)
#         self._list_discussion_comments_helper()
#         self.logout()
#         self.login(**stu_cred)
#         self._list_discussion_comments_helper()
#         self.logout()

#     def _retrieve_discussion_comment_helper(self):
#         """Helper function to test retreive discussion comment functionality."""
#         discussion_comment_id = 1
#         url = reverse(
#             "discussion_forum:discussioncomment-retrieve-discussion-comment",
#             kwargs={"pk": discussion_comment_id},
#         )
#         response = self.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["id"], discussion_comment_id)

#     def test_retrieve_discussion_comment(self):
#         """Test to check: retrieve discussion_comment."""
#         self.login(**ins_cred)
#         self._retrieve_discussion_comment_helper()
#         self.logout()
#         self.login(**ta_cred)
#         self._retrieve_discussion_comment_helper()
#         self.logout()
#         self.login(**stu_cred)
#         self._retrieve_discussion_comment_helper()
#         self.logout()

#     def _create_discussion_comment_helper(
#         self, status_code, author_id, author_category
#     ):
#         """Helper function to test create discussion comment functionality.

#         Args:
#             status_code (int): expected status code of the API call
#             author_id (int): user id
#             author_category (char): user category(inst/stud/ta)
#         """
#         data = {
#             "discussion_thread": 1,
#             "author": author_id,
#             "author_category": author_category,
#             "description": "Description of discussion comment",
#             "pinned": True,
#             "anonymous_to_student": True,
#             "upvote": 0,
#             "downvote": 0,
#         }
#         url = reverse("discussion_forum:discussioncomment-create-discussion-comment")
#         response = self.post(url, data)
#         self.assertEqual(response.status_code, status_code)
#         if status_code == status.HTTP_201_CREATED:
#             response_data = response.data
#             for field in [
#                 "created_on",
#                 "modified_on",
#                 "id",
#             ]:
#                 response_data.pop(field)
#             self.assertEqual(response_data, data)

#     def test_create_discussion_comment(self):
#         """Test to check: create a discussion comment."""
#         self.login(**ins_cred)
#         self._create_discussion_comment_helper(status.HTTP_201_CREATED, 1, "I")
#         self.logout()
#         self.login(**ta_cred)
#         self._create_discussion_comment_helper(status.HTTP_201_CREATED, 2, "T")
#         self.logout()
#         self.login(**stu_cred)
#         self._create_discussion_comment_helper(status.HTTP_201_CREATED, 3, "S")
#         self.logout()

#     def _update_discussion_comment_helper(
#         self, status_code, author_id, author_category
#     ):
#         """
#         Helper function to test update discussion comment functionality.

#         Args:
#             status_code (int): expected status code of the API call
#             author_id (int): user id
#             author_category (char): user category(inst/stud/ta)
#         """
#         discussion_comment = DiscussionComment(
#             discussion_thread_id=1,
#             author_id=author_id,
#             author_category=author_category,
#             description="This is discussion comment",
#         )
#         discussion_comment.save()
#         data = {
#             "discussion_thread": 1,
#             "author": author_id,
#             "author_category": author_category,
#             "description": "Description of discussion comment",
#             "pinned": True,
#             "anonymous_to_student": True,
#             "upvote": 0,
#             "downvote": 0,
#         }
#         url = reverse(
#             ("discussion_forum:discussioncomment-update-discussion-comment"),
#             kwargs={"pk": discussion_comment.id},
#         )
#         response = self.put(url, data)
#         self.assertEqual(response.status_code, status_code)
#         if status_code == status.HTTP_200_OK:
#             response_data = response.data
#             for field in [
#                 "created_on",
#                 "modified_on",
#                 "id",
#             ]:
#                 response_data.pop(field)
#             self.assertEqual(response_data, data)

#     def test_update_discussion_comment(self):
#         """Test to check: Update discussion comment."""
#         self.login(**ins_cred)
#         self._update_discussion_comment_helper(status.HTTP_200_OK, 1, "I")
#         self.logout()
#         self.login(**ta_cred)
#         self._update_discussion_comment_helper(status.HTTP_200_OK, 2, "T")
#         self.logout()
#         self.login(**stu_cred)
#         self._update_discussion_comment_helper(status.HTTP_200_OK, 3, "S")
#         self.logout()

#     def _partial_update_discussion_comment_helper(
#         self, status_code, author_id, author_category
#     ):
#         """
#         Helper function to test partial update discussion comment functionality.

#         Args:
#             status_code (int): expected status code of the API call
#             author_id (int): user id
#             author_category (char): user category(inst/stud/ta)
#         """
#         discussion_comment = DiscussionComment(
#             discussion_thread_id=1,
#             author_id=author_id,
#             author_category=author_category,
#             description="This is the comment description",
#         )
#         discussion_comment.save()
#         data = {
#             "description": "changed description",
#         }
#         url = reverse(
#             ("discussion_forum:discussioncomment-update-discussion-comment"),
#             kwargs={"pk": discussion_comment.id},
#         )
#         response = self.put(url, data)
#         self.assertEqual(response.status_code, status_code)
#         if status_code == status.HTTP_200_OK:
#             response_data = response.data
#             self.assertEqual(response_data["description"], data["description"])

#     def test_partial_update_discussion_comment(self):
#         """
#         Test to check: partial update a discussion comment.
#         """
#         self.login(**ins_cred)
#         self._partial_update_discussion_comment_helper(status.HTTP_200_OK, 1, "I")
#         self.logout()
#         self.login(**ta_cred)
#         self._partial_update_discussion_comment_helper(status.HTTP_200_OK, 2, "T")
#         self.logout()
#         self.login(**stu_cred)
#         self._partial_update_discussion_comment_helper(status.HTTP_200_OK, 3, "S")
#         self.logout()


# class DiscussionReplyViewSetTest(APITestCase):
#     """Test for DiscussionReplyViewSet."""

#     fixtures = [
#         "users.test.yaml",
#         "colleges.test.yaml",
#         "departments.test.yaml",
#         "chapters.test.yaml",
#         "sections.test.yaml",
#         "documents.test.yaml",
#         "courses.test.yaml",
#         "coursehistories.test.yaml",
#         "videos.test.yaml",
#         "discussionforum.tests.yaml",
#         "tags.test.yaml",
#         "discussionthread.tests.yaml",
#         "discussioncomment.test.yaml",
#         "discussionreply.test.yaml",
#     ]

#     def _list_discussion_replies_helper(self):
#         """Helper function to test list discussion replies functionality."""
#         discussion_comment_id = 1
#         url = reverse(
#             "discussion_forum:discussionreply-list-discussion-replies",
#             args=[discussion_comment_id],
#         )
#         response = self.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(
#             len(response.data["results"]), DiscussionReply.objects.all().count()
#         )

#     def test_list_discussion_replies(self):
#         """Test to check: list all discussion replies."""
#         self.login(**ins_cred)
#         self._list_discussion_replies_helper()
#         self.logout()
#         self.login(**ta_cred)
#         self._list_discussion_replies_helper()
#         self.logout()
#         self.login(**stu_cred)
#         self._list_discussion_replies_helper()
#         self.logout()

#     def _retrieve_discussion_reply_helper(self):
#         """Helper function to test retrive discussion reply functionality."""
#         discussion_reply_id = 1
#         url = reverse(
#             "discussion_forum:discussionreply-retrieve-discussion-reply",
#             kwargs={"pk": discussion_reply_id},
#         )
#         response = self.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["id"], discussion_reply_id)

#     def test_retrieve_discussion_reply(self):
#         """Test to check: retrieve discussion_reply."""
#         self.login(**ins_cred)
#         self._retrieve_discussion_reply_helper()
#         self.logout()
#         self.login(**ta_cred)
#         self._retrieve_discussion_reply_helper()
#         self.logout()
#         self.login(**stu_cred)
#         self._retrieve_discussion_reply_helper()
#         self.logout()

#     def _create_discussion_reply_helper(self, status_code,
#            author_id, author_category):
#         """Helper function to test create discussion reply functionality.

#         Args:
#             status_code (int): expected status code of the API call
#             author_id (int): user id
#             author_category (char): user category(inst/stud/ta)
#         """
#         data = {
#             "discussion_comment": 1,
#             "author": author_id,
#             "author_category": author_category,
#             "description": "Description of discussion reply",
#             "pinned": True,
#             "anonymous_to_student": True,
#             "upvote": 0,
#             "downvote": 0,
#         }
#         url = reverse("discussion_forum:discussionreply-create-discussion-reply")
#         response = self.post(url, data)
#         self.assertEqual(response.status_code, status_code)
#         if status_code == status.HTTP_201_CREATED:
#             response_data = response.data
#             for field in [
#                 "created_on",
#                 "modified_on",
#                 "id",
#             ]:
#                 response_data.pop(field)
#             self.assertEqual(response_data, data)

#     def test_create_discussion_reply(self):
#         """Test to check: create a discussion reply."""
#         self.login(**ins_cred)
#         self._create_discussion_reply_helper(status.HTTP_201_CREATED, 1, "I")
#         self.logout()
#         self.login(**ins_cred)
#         self._create_discussion_reply_helper(status.HTTP_201_CREATED, 2, "T")
#         self.logout()
#         self.login(**ins_cred)
#         self._create_discussion_reply_helper(status.HTTP_201_CREATED, 3, "S")
#         self.logout()

#     def _update_discussion_reply_helper(self, status_code,
#            author_id, author_category):
#         """
#         Helper function to test update discussion reply functionality.

#         Args:
#             status_code (int): expected status code of the API call
#             author_id (int): user id
#             author_category (char): user category(inst/stud/ta)
#         """
#         discussion_reply = DiscussionReply(
#             discussion_comment_id=1,
#             author_id=author_id,
#             author_category=author_category,
#             description="This is des reply",
#         )
#         discussion_reply.save()
#         data = {
#             "discussion_comment": 1,
#             "author": author_id,
#             "author_category": author_category,
#             "description": "Description of discussion comment",
#             "pinned": True,
#             "anonymous_to_student": True,
#             "upvote": 0,
#             "downvote": 0,
#         }
#         url = reverse(
#             ("discussion_forum:discussionreply-update-discussion-reply"),
#             kwargs={"pk": discussion_reply.id},
#         )
#         response = self.put(url, data)
#         self.assertEqual(response.status_code, status_code)
#         if status_code == status.HTTP_200_OK:
#             response_data = response.data
#             for field in [
#                 "created_on",
#                 "modified_on",
#                 "id",
#             ]:
#                 response_data.pop(field)
#             self.assertEqual(response_data, data)

#     def test_update_discussion_reply(self):
#         """Test to check: Update discussion reply functionality."""
#         self.login(**ins_cred)
#         self._update_discussion_reply_helper(status.HTTP_200_OK, 1, "I")
#         self.logout()
#         self.login(**ta_cred)
#         self._update_discussion_reply_helper(status.HTTP_200_OK, 2, "T")
#         self.logout()
#         self.login(**stu_cred)
#         self._update_discussion_reply_helper(status.HTTP_200_OK, 3, "S")
#         self.logout()

#     def _partial_update_discussion_reply_helper(
#         self, status_code, author_id, author_category
#     ):
#         """
#         Helper function to test partial update discussion reply functionality.

#         Args:
#             status_code (int): expected status code of the API call
#             author_id (int): user id
#             author_category (char): user category(inst/stud/ta)
#         """
#         discussion_reply = DiscussionReply(
#             discussion_comment_id=1,
#             author_id=author_id,
#             author_category=author_category,
#             description="This the reply description",
#         )
#         discussion_reply.save()
#         data = {
#             "description": "changed description",
#         }
#         url = reverse(
#             ("discussion_forum:discussionreply-update-discussion-reply"),
#             kwargs={"pk": discussion_reply.id},
#         )
#         response = self.put(url, data)
#         self.assertEqual(response.status_code, status_code)
#         if status_code == status.HTTP_200_OK:
#             response_data = response.data
#             self.assertEqual(response_data["description"], data["description"])

#     def test_partial_update_discussion_reply(self):
#         """Test to check: Partial update discussion reply functionality."""
#         self.login(**ins_cred)
#         self._partial_update_discussion_reply_helper(status.HTTP_200_OK, 1, "I")
#         self.logout()
#         self.login(**ta_cred)
#         self._partial_update_discussion_reply_helper(status.HTTP_200_OK, 2, "T")
#         self.logout()
#         self.login(**stu_cred)
#         self._partial_update_discussion_reply_helper(status.HTTP_200_OK, 3, "S")
#         self.logout()
