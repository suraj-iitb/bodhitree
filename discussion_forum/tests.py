from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .models import DiscussionComment, DiscussionThread


ins_cred = {"email": "instructor@bodhitree.com", "password": "instructor"}
ta_cred = {"email": "ta@bodhitree.com", "password": "ta"}
stu_cred = {"email": "student@bodhitree.com", "password": "student"}


class DiscussionThreadViewSetTest(APITestCase):
    """Test for DiscussionThreadViewSet."""

    fixtures = [
        "users.test.yaml",
        "colleges.test.yaml",
        "departments.test.yaml",
        "chapters.test.yaml",
        "sections.test.yaml",
        "documents.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "videos.test.yaml",
        "discussionforum.tests.yaml",
        "tags.test.yaml",
        "discussionthread.tests.yaml",
    ]

    def _list_discussion_threads_helper(self):
        """Helper function to test list discussion threads functionality."""
        discussion_forum_id = 1
        url = reverse(
            "discussion_forum:discussionthread-list-discussion-threads",
            args=[discussion_forum_id],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data["results"]), DiscussionThread.objects.all().count()
        )

    def test_list_discussion_threads(self):
        """Test to check: list all discussion_threads."""
        self.client.login(**ins_cred)
        self._list_discussion_threads_helper()
        self.client.logout()
        self.client.login(**ta_cred)
        self._list_discussion_threads_helper()
        self.client.logout()
        self.client.login(**stu_cred)
        self._list_discussion_threads_helper()
        self.client.logout()

    def _retrieve_discussion_thread_helper(self):
        """Helper function to test retrieve discussion thread functionality."""
        discussion_thread_id = 1
        url = reverse(
            "discussion_forum:discussionthread-retrieve-discussion-thread",
            args=[discussion_thread_id],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], discussion_thread_id)

    def test_retrieve_discussion_thread(self):
        """Test to check: retrieve discussion_thread."""
        self.client.login(**ins_cred)
        self._retrieve_discussion_thread_helper()
        self.client.logout()
        self.client.login(**ta_cred)
        self._retrieve_discussion_thread_helper()
        self.client.logout()
        self.client.login(**stu_cred)
        self._retrieve_discussion_thread_helper()
        self.client.logout()

    def _create_discussion_thread_helper(
        self, title, status_code, author_id, author_category
    ):
        """helper function to test create discussion thread functionality.

        Args:
            title (str): title of the discussion thread
            status_code (int): expected status code of the API call
            author_id (int): user id
            author_category (char): user category(inst/stud/ta)
        """
        data = {
            "discussion_forum": 1,
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
        """Test to check: create a discussion thread."""
        self.client.login(**ins_cred)
        self._create_discussion_thread_helper(
            "DiscussionThread 1", status.HTTP_201_CREATED, 1, "I"
        )
        self.client.logout()
        self.client.login(**ta_cred)
        self._create_discussion_thread_helper(
            "DiscussionThread 2", status.HTTP_201_CREATED, 2, "T"
        )
        self.client.logout()
        self.client.login(**stu_cred)
        self._create_discussion_thread_helper(
            "DiscussionThread 3", status.HTTP_201_CREATED, 3, "S"
        )
        self.client.logout()

    def _update_discussion_thread_helper(
        self, title, status_code, author_id, author_category
    ):
        """
        Helper function to test update discussion thread functionality.

        Args:
            status_code (int): expected status code of the API call
            title (str): title of the discussion thread
            author_id (int): user id
            author_category (char): user category(inst/stud/ta)
        """
        discussion_thread = DiscussionThread(
            title="DiscussionThread 4",
            discussion_forum_id=1,
            author_id=author_id,
            author_category=author_category,
        )
        discussion_thread.save()
        data = {
            "discussion_forum": 1,
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
        response = self.client.put(url, data)
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

    def test_update_discussion_thread(self):
        """Test to check: Update discussion thread functionality."""
        self.client.login(**ins_cred)
        self._update_discussion_thread_helper(
            "DiscussionThread 5", status.HTTP_200_OK, 1, "I"
        )
        self.client.logout()
        self.client.login(**ta_cred)
        self._update_discussion_thread_helper(
            "DiscussionThread 6", status.HTTP_200_OK, 2, "T"
        )
        self.client.logout()
        self.client.login(**stu_cred)
        self._update_discussion_thread_helper(
            "DiscussionThread 7", status.HTTP_200_OK, 3, "S"
        )
        self.client.logout()

    def _partial_update_discussion_thread_helper(
        self, title, status_code, author_id, author_category
    ):
        """
        Helper function to test partial update discussion thread functionality.

        Args:
            status_code (int): expected status code of the API call
            title (str): title of the discussion thread
            author_id (int): user id
            author_category (char): user category
        """
        discussion_thread = DiscussionThread(
            title="DiscussionThread 8",
            discussion_forum_id=1,
            author_id=author_id,
            author_category=author_category,
        )
        discussion_thread.save()
        data = {
            "title": title,
        }
        url = reverse(
            ("discussion_forum:discussionthread-update-discussion-thread"),
            kwargs={"pk": discussion_thread.id},
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            self.assertEqual(return_data["title"], data["title"])

    def test_partial_update_discussion_thread(self):
        """Test to check: Partial update discussion thread functionality."""
        self.client.login(**ins_cred)
        self._partial_update_discussion_thread_helper(
            "DiscussionThread 9", status.HTTP_200_OK, 1, "I"
        )
        self.client.logout()
        self.client.login(**ta_cred)
        self._partial_update_discussion_thread_helper(
            "DiscussionThread 10", status.HTTP_200_OK, 2, "T"
        )
        self.client.logout()
        self.client.login(**stu_cred)
        self._partial_update_discussion_thread_helper(
            "DiscussionThread 11", status.HTTP_200_OK, 3, "S"
        )
        self.client.logout()


class DiscussionCommentViewSetTest(APITestCase):
    """Test for DiscussionCommentViewSet."""

    fixtures = [
        "users.test.yaml",
        "colleges.test.yaml",
        "departments.test.yaml",
        "chapters.test.yaml",
        "sections.test.yaml",
        "documents.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "videos.test.yaml",
        "discussionforum.tests.yaml",
        "tags.test.yaml",
        "discussionthread.tests.yaml",
        "discussioncomment.test.yaml",
    ]

    def _list_discussion_comments_helper(self):
        """Helper function to test list discussion comments functionality."""
        discussion_thread_id = 1
        url = reverse(
            "discussion_forum:discussioncomment-list-discussion-comments",
            args=[discussion_thread_id],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), DiscussionComment.objects.all().count())

    def test_list_discussion_comments(self):
        """Test to check: list all discussion_comments."""
        self.client.login(**ins_cred)
        self._list_discussion_comments_helper()
        self.client.logout()
        self.client.login(**ta_cred)
        self._list_discussion_comments_helper()
        self.client.logout()
        self.client.login(**stu_cred)
        self._list_discussion_comments_helper()
        self.client.logout()

    def _retrieve_discussion_comment_helper(self):
        """Helper function to test retreive discussion comment functionality."""
        discussion_comment_id = 1
        url = reverse(
            "discussion_forum:discussioncomment-retrieve-discussion-comment",
            kwargs={"pk": discussion_comment_id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], discussion_comment_id)

    def test_retrieve_discussion_comment(self):
        """Test to check: retrieve discussion_comment."""
        self.client.login(**ins_cred)
        self._retrieve_discussion_comment_helper()
        self.client.logout()
        self.client.login(**ta_cred)
        self._retrieve_discussion_comment_helper()
        self.client.logout()
        self.client.login(**stu_cred)
        self._retrieve_discussion_comment_helper()
        self.client.logout()

    def _create_discussion_comment_helper(
        self, status_code, author_id, author_category
    ):
        """Helper function to test create discussion comment functionality.

        Args:
            status_code (int): expected status code of the API call
            author_id (int): user id
            author_category (char): user category(inst/stud/ta)
        """
        data = {
            "discussion_thread": 1,
            "author": author_id,
            "author_category": author_category,
            "description": "Description of discussion comment",
            "pinned": True,
            "anonymous_to_student": True,
            "upvote": 0,
            "downvote": 0,
        }
        url = reverse("discussion_forum:discussioncomment-create-discussion-comment")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            for field in [
                "created_on",
                "modified_on",
                "id",
            ]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def test_create_discussion_comment(self):
        """Test to check: create a discussion comment."""
        self.client.login(**ins_cred)
        self._create_discussion_comment_helper(status.HTTP_201_CREATED, 1, "I")
        self.client.logout()
        self.client.login(**ta_cred)
        self._create_discussion_comment_helper(status.HTTP_201_CREATED, 2, "T")
        self.client.logout()
        self.client.login(**stu_cred)
        self._create_discussion_comment_helper(status.HTTP_201_CREATED, 3, "S")
        self.client.logout()

    def _update_discussion_comment_helper(
        self, status_code, author_id, author_category
    ):
        """
        Helper function to test update discussion comment functionality.

        Args:
            status_code (int): expected status code of the API call
            author_id (int): user id
            author_category (char): user category(inst/stud/ta)
        """
        discussion_comment = DiscussionComment(
            discussion_thread_id=1,
            author_id=author_id,
            author_category=author_category,
            description="This is discussion comment",
        )
        discussion_comment.save()
        data = {
            "discussion_thread": 1,
            "author": author_id,
            "author_category": author_category,
            "description": "Description of discussion comment",
            "pinned": True,
            "anonymous_to_student": True,
            "upvote": 0,
            "downvote": 0,
        }
        url = reverse(
            ("discussion_forum:discussioncomment-update-discussion-comment"),
            kwargs={"pk": discussion_comment.id},
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            for field in [
                "created_on",
                "modified_on",
                "id",
            ]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def test_update_discussion_comment(self):
        """Test to check: Update discussion comment."""
        self.client.login(**ins_cred)
        self._update_discussion_comment_helper(status.HTTP_200_OK, 1, "I")
        self.client.logout()
        self.client.login(**ta_cred)
        self._update_discussion_comment_helper(status.HTTP_200_OK, 2, "T")
        self.client.logout()
        self.client.login(**stu_cred)
        self._update_discussion_comment_helper(status.HTTP_200_OK, 3, "S")
        self.client.logout()

    def _partial_update_discussion_comment_helper(
        self, status_code, author_id, author_category
    ):
        """
        Helper function to test partial update discussion comment functionality.

        Args:
            status_code (int): expected status code of the API call
            author_id (int): user id
            author_category (char): user category(inst/stud/ta)
        """
        discussion_comment = DiscussionComment(
            discussion_thread_id=1,
            author_id=author_id,
            author_category=author_category,
            description="This is the comment description",
        )
        discussion_comment.save()
        data = {
            "description": "changed description",
        }
        url = reverse(
            ("discussion_forum:discussioncomment-update-discussion-comment"),
            kwargs={"pk": discussion_comment.id},
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            self.assertEqual(return_data["description"], data["description"])

    def test_partial_update_discussion_comment(self):
        """
        Test to check: partial update a discussion comment.
        """
        self.client.login(**ins_cred)
        self._partial_update_discussion_comment_helper(status.HTTP_200_OK, 1, "I")
        self.client.logout()
        self.client.login(**ta_cred)
        self._partial_update_discussion_comment_helper(status.HTTP_200_OK, 2, "T")
        self.client.logout()
        self.client.login(**stu_cred)
        self._partial_update_discussion_comment_helper(status.HTTP_200_OK, 3, "S")
        self.client.logout()


# class DiscussionReplyViewSetTest(APITestCase):
#     """Test for DiscussionReplyViewSet."""

#     fixtures = [
#         "users.test.yaml",
#         "courses.test.yaml",
#         "coursehistories.test.yaml",
#         "discussionforum.tests.yaml",
#         "discussionthread.tests.yaml",
#         "discussioncomment.test.yaml",
#         "discussionreply.test.yaml",
#     ]

#     def _list_discussion_replies_helper(self):
#         """helper function to test list discussion replies functionality."""

#         url = reverse(
#             "discussion_forum:discussionreply-list-discussion-replies", args=[1]
#         )
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         length = DiscussionReply.objects.all().count()
#         self.assertEqual(len(response.data), length)

#     def test_list_discussion_replies(self):
#         """
#         Test to check: list all discussion_replies.
#         """
#         self.client.login(**ins_cred)
#         self._list_discussion_replies_helper()
#         self.client.logout()

#     def _retrieve_discussion_reply_helper(self, discussion_reply_id):
#         """helper function to test retrive discussion reply functionality."""

#         url = reverse(
#             "discussion_forum:discussionreply-retrieve-discussion-reply",
#             kwargs={"pk": discussion_reply_id},
#         )
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["id"], discussion_reply_id)

#     def test_retrieve_discussion_reply(self):
#         """
#         Test to check: retrieve discussion_reply.
#         """
#         discussion_reply_id = 1
#         self.client.login(**ins_cred)
#         self._retrieve_discussion_reply_helper(discussion_reply_id)
#         self.client.logout()

#     def _create_discussion_reply_helper(self, status_code):
#         """helper function to test create discussion reply functionality.

#         Args:
#         status_code (int): expected status code of the API call
#         """

#         data = {
#             "discussion_comment": 1,
#             "author": 1,
#             "author_category": "I",
#             "description": "Description of discussion reply",
#             "pinned": True,
#             "anonymous_to_student": True,
#             "upvote": 0,
#             "downvote": 0,
#         }
#         url = reverse(
#             "discussion_forum:discussionreply-create-discussion-reply", args=[1]
#         )
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status_code)
#         if status_code == status.HTTP_201_CREATED:
#             return_data = response.data
#             for k in [
#                 "created_on",
#                 "modified_on",
#                 "id",
#             ]:
#                 return_data.pop(k)
#             self.assertEqual(return_data, data)

#     def test_create_discussion_reply(self):
#         """
#         test to check: create a discussion reply.
#         """
#         self.client.login(**ins_cred)
#         self._create_discussion_reply_helper(status.HTTP_201_CREATED)
#         self.client.logout()

#     def _update_discussion_reply_helper(self, status_code):
#         """
#         Helper function to test update discussion reply functionality.

#         Args:
#         status_code (int): expected status code of the API call
#         """

#         discussion_reply1 = DiscussionReply(
#             discussion_comment_id=1,
#             author_id=1,
#             author_category="I",
#             description="This is des reply",
#         )
#         discussion_reply1.save()
#         data = {
#             "discussion_comment": 1,
#             "author": 1,
#             "author_category": "I",
#             "description": "Description of discussion comment",
#             "pinned": True,
#             "anonymous_to_student": True,
#             "upvote": 0,
#             "downvote": 0,
#         }
#         url = reverse(
#             ("discussion_forum:discussionreply-update-discussion-reply"),
#             kwargs={"pk": discussion_reply1.id},
#         )
#         response = self.client.put(url, data)
#         self.assertEqual(response.status_code, status_code)
#         if status_code == status.HTTP_200_OK:
#             return_data = response.data
#             for k in [
#                 "created_on",
#                 "modified_on",
#                 "id",
#             ]:
#                 return_data.pop(k)
#             self.assertEqual(return_data, data)

#     def test_update_discussion_reply(self):
#         """
#         Test to check: Update discussion reply functionality.
#         """
#         self.client.login(**ins_cred)
#         self._update_discussion_reply_helper(status.HTTP_200_OK)
#         self.client.logout()

#     def _partial_update_discussion_reply_helper(self, status_code):
#         """
#         Helper function to test partial update discussion reply functionality.

#         Args:
#         status_code (int): expected status code of the API call
#         """
#         discussion_reply1 = DiscussionReply(
#             discussion_comment_id=1,
#             author_id=1,
#             author_category="I",
#             description="This the reply des 2",
#         )
#         discussion_reply1.save()
#         data = {
#             "description": "changed description",
#         }
#         url = reverse(
#             ("discussion_forum:discussionreply-update-discussion-reply"),
#             kwargs={"pk": discussion_reply1.id},
#         )
#         response = self.client.put(url, data)
#         self.assertEqual(response.status_code, status_code)
#         if status_code == status.HTTP_200_OK:
#             return_data = response.data
#             for k in [
#                 "discussion_comment",
#                 "author",
#                 "author_category",
#                 "pinned",
#                 "anonymous_to_student",
#                 "upvote",
#                 "downvote",
#                 "created_on",
#                 "modified_on",
#                 "id",
#             ]:
#                 return_data.pop(k)
#             self.assertEqual(return_data, data)

#     def test_partial_update_discussion_reply(self):
#         """
#         Ensure we can partial update an existing DiscussionReply object.
#         """
#         self.client.login(**ins_cred)
#         self._partial_update_discussion_reply_helper(status.HTTP_200_OK)
#         self.client.logout()
