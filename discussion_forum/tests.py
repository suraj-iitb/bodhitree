from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .models import DiscussionComment, DiscussionReply, DiscussionThread


ins_cred = {"email": "instructor@bodhitree.com", "password": "instructor"}


class DiscussionThreadViewSetTest(APITestCase):
    fixtures = [
        "users.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "discussionforum.tests.yaml",
        "discussionthread.tests.yaml",
    ]

    def get_discussion_threads_helper(self):
        url = reverse(
            "discussion_forum:discussionthread-list-discussion-threads", args=[1]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        length = DiscussionThread.objects.all().count()
        self.assertEqual(len(response.data), length)

    def test_get_discussion_threads(self):
        """
        Ensure we can get all DiscussionThreads objects.
        """
        self.client.login(**ins_cred)
        self.get_discussion_threads_helper()
        self.client.logout()

    def get_discussion_thread_helper(self, discussion_thread_id):
        url = reverse(
            "discussion_forum:discussionthread-retrieve-discussion-thread",
            kwargs={"pk": discussion_thread_id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)

    def test_get_discussion_thread(self):
        """
        Ensure we can get one DiscussionThread object.
        """
        discussion_thread_id = 1
        self.client.login(**ins_cred)
        self.get_discussion_thread_helper(discussion_thread_id)
        self.client.logout()

    def create_discussion_thread_helper(self, title, status_code):
        data = {
            "discussion_forum": 1,
            "title": title,
            "mark_as_important": True,
            "author": 1,
            "author_category": "I",
            "description": "Description of discussion thread",
            "pinned": True,
            "anonymous_to_student": True,
            "upvote": 0,
            "downvote": 0,
        }
        url = reverse(
            "discussion_forum:discussionthread-create-discussion-thread", args=[1]
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            return_data = response.data
            for k in [
                "created_on",
                "modified_on",
                "id",
                "tag",
            ]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_create_discussion_thread(self):
        """
        Ensure we can create a new 'DiscussionThread' object
        """
        self.client.login(**ins_cred)
        self.create_discussion_thread_helper("Thread1", status.HTTP_201_CREATED)
        self.client.logout()

    def update_discussion_thread_helper(self, title, status_code):
        discussion_thread1 = DiscussionThread(
            title="DiscussionThread77",
            discussion_forum_id=1,
            author_id=1,
            author_category="I",
        )
        discussion_thread1.save()
        data = {
            "discussion_forum": 1,
            "title": title,
            "mark_as_important": True,
            "author": 1,
            "author_category": "I",
            "description": "Description of discussion thread",
            "pinned": True,
            "anonymous_to_student": True,
            "upvote": 0,
            "downvote": 0,
        }
        url = reverse(
            ("discussion_forum:discussionthread-update-discussion-thread"),
            kwargs={"pk": discussion_thread1.id},
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for k in [
                "created_on",
                "modified_on",
                "id",
                "tag",
            ]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_update_discussion_thread(self):
        """
        Ensure we can update an existing DiscussionThread object.
        """
        self.client.login(**ins_cred)
        self.update_discussion_thread_helper("DiscussionThread78", status.HTTP_200_OK)
        self.client.logout()

    def partial_update_discussion_thread_helper(self, title, status_code):
        discussion_thread1 = DiscussionThread(
            title="DiscussionThread79",
            discussion_forum=1,
            author=1,
            author_category="I",
        )
        discussion_thread1.save()
        data = {
            "title": title,
        }
        url = reverse(
            ("discussion_forum:discussionthread-update-discussion-thread"),
            kwargs={"pk": discussion_thread1.id},
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for k in [
                "discussion_forum",
                "mark_as_important",
                "author",
                "author_category",
                "description",
                "pinned",
                "anonymous_to_student",
                "upvote",
                "downvote" "created_on",
                "modified_on",
                "id",
                "tag",
            ]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_partial_update_discussion_thread(self):
        """
        Ensure we can partial update an existing DiscussionThread object.
        """
        self.client.login(**ins_cred)
        self.update_discussion_thread_helper("DiscussionThread78", status.HTTP_200_OK)
        self.client.logout()


class DiscussionCommentViewSetTest(APITestCase):
    fixtures = [
        "users.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "discussionforum.tests.yaml",
        "discussionthread.tests.yaml",
        "discussioncomment.test.yaml",
    ]

    def get_discussion_comments_helper(self):
        url = reverse(
            "discussion_forum:discussioncomment-list-discussion-comments", args=[1]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        length = DiscussionThread.objects.all().count()
        self.assertEqual(len(response.data), length)

    def test_get_discussion_comments(self):
        """
        Ensure we can get all DiscussionComments objects.
        """
        self.client.login(**ins_cred)
        self.get_discussion_comments_helper()
        self.client.logout()

    def get_discussion_comment_helper(self, discussion_comment_id):
        url = reverse(
            "discussion_forum:discussioncomment-retrieve-discussion-comment",
            kwargs={"pk": discussion_comment_id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)

    def test_get_discussion_comment(self):
        """
        Ensure we can get one DiscussionComment object.
        """
        discussion_comment_id = 1
        self.client.login(**ins_cred)
        self.get_discussion_comment_helper(discussion_comment_id)
        self.client.logout()

    def create_discussion_comment_helper(self, status_code):
        data = {
            "discussion_thread": 1,
            "author": 1,
            "author_category": "I",
            "description": "Description of discussion comment",
            "pinned": True,
            "anonymous_to_student": True,
            "upvote": 0,
            "downvote": 0,
        }
        url = reverse(
            "discussion_forum:discussioncomment-create-discussion-comment", args=[1]
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            return_data = response.data
            for k in [
                "created_on",
                "modified_on",
                "id",
            ]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_create_discussion_comment(self):
        """
        Ensure we can create a new 'DiscussionComment' object
        """
        self.client.login(**ins_cred)
        self.create_discussion_comment_helper(status.HTTP_201_CREATED)
        self.client.logout()

    def update_discussion_comment_helper(self, status_code):
        discussion_comment1 = DiscussionComment(
            discussion_thread_id=1,
            author_id=1,
            author_category="I",
            description="This is des comment",
        )
        discussion_comment1.save()
        data = {
            "discussion_thread": 1,
            "author": 1,
            "author_category": "I",
            "description": "Description of discussion comment",
            "pinned": True,
            "anonymous_to_student": True,
            "upvote": 0,
            "downvote": 0,
        }
        url = reverse(
            ("discussion_forum:discussioncomment-update-discussion-comment"),
            kwargs={"pk": discussion_comment1.id},
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for k in [
                "created_on",
                "modified_on",
                "id",
            ]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_update_discussion_comment(self):
        """
        Ensure we can update an existing DiscussionComment object.
        """
        self.client.login(**ins_cred)
        self.update_discussion_comment_helper(status.HTTP_200_OK)
        self.client.logout()

    def partial_update_discussion_comment_helper(self, status_code):
        discussion_comment1 = DiscussionComment(
            discussion_thread_id=1,
            author_id=1,
            author_category="I",
            description="This the comment des 2",
        )
        discussion_comment1.save()
        data = {
            "description": "changed description",
        }
        url = reverse(
            ("discussion_forum:discussioncomment-update-discussion-comment"),
            kwargs={"pk": discussion_comment1.id},
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for k in [
                "discussion_thread",
                "author",
                "author_category",
                "pinned",
                "anonymous_to_student",
                "upvote",
                "downvote",
                "created_on",
                "modified_on",
                "id",
            ]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_partial_update_discussion_comment(self):
        """
        Ensure we can partial update an existing DiscussionComment object.
        """
        self.client.login(**ins_cred)
        self.partial_update_discussion_comment_helper(status.HTTP_200_OK)
        self.client.logout()


class DiscussionReplyViewSetTest(APITestCase):
    fixtures = [
        "users.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "discussionforum.tests.yaml",
        "discussionthread.tests.yaml",
        "discussioncomment.test.yaml",
        "discussionreply.test.yaml",
    ]

    def get_discussion_replies_helper(self):
        url = reverse(
            "discussion_forum:discussionreply-list-discussion-replies", args=[1]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        length = DiscussionReply.objects.all().count()
        self.assertEqual(len(response.data), length)

    def test_get_discussion_replies(self):
        """
        Ensure we can get all DiscussionReplies objects.
        """
        self.client.login(**ins_cred)
        self.get_discussion_replies_helper()
        self.client.logout()

    def get_discussion_reply_helper(self, discussion_reply_id):
        url = reverse(
            "discussion_forum:discussionreply-retrieve-discussion-reply",
            kwargs={"pk": discussion_reply_id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)

    def test_get_discussion_reply(self):
        """
        Ensure we can get one DiscussionReply object.
        """
        discussion_reply_id = 1
        self.client.login(**ins_cred)
        self.get_discussion_reply_helper(discussion_reply_id)
        self.client.logout()

    def create_discussion_reply_helper(self, status_code):
        data = {
            "discussion_comment": 1,
            "author": 1,
            "author_category": "I",
            "description": "Description of discussion reply",
            "pinned": True,
            "anonymous_to_student": True,
            "upvote": 0,
            "downvote": 0,
        }
        url = reverse(
            "discussion_forum:discussionreply-create-discussion-reply", args=[1]
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            return_data = response.data
            for k in [
                "created_on",
                "modified_on",
                "id",
            ]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_create_discussion_reply(self):
        """
        Ensure we can create a new 'DiscussionReply' object
        """
        self.client.login(**ins_cred)
        self.create_discussion_reply_helper(status.HTTP_201_CREATED)
        self.client.logout()

    def update_discussion_reply_helper(self, status_code):
        discussion_reply1 = DiscussionReply(
            discussion_comment_id=1,
            author_id=1,
            author_category="I",
            description="This is des reply",
        )
        discussion_reply1.save()
        data = {
            "discussion_comment": 1,
            "author": 1,
            "author_category": "I",
            "description": "Description of discussion comment",
            "pinned": True,
            "anonymous_to_student": True,
            "upvote": 0,
            "downvote": 0,
        }
        url = reverse(
            ("discussion_forum:discussionreply-update-discussion-reply"),
            kwargs={"pk": discussion_reply1.id},
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for k in [
                "created_on",
                "modified_on",
                "id",
            ]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_update_discussion_reply(self):
        """
        Ensure we can update an existing DiscussionReply object.
        """
        self.client.login(**ins_cred)
        self.update_discussion_reply_helper(status.HTTP_200_OK)
        self.client.logout()

    def partial_update_discussion_reply_helper(self, status_code):
        discussion_reply1 = DiscussionReply(
            discussion_comment_id=1,
            author_id=1,
            author_category="I",
            description="This the reply des 2",
        )
        discussion_reply1.save()
        data = {
            "description": "changed description",
        }
        url = reverse(
            ("discussion_forum:discussionreply-update-discussion-reply"),
            kwargs={"pk": discussion_reply1.id},
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for k in [
                "discussion_comment",
                "author",
                "author_category",
                "pinned",
                "anonymous_to_student",
                "upvote",
                "downvote",
                "created_on",
                "modified_on",
                "id",
            ]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_partial_update_discussion_reply(self):
        """
        Ensure we can partial update an existing DiscussionReply object.
        """
        self.client.login(**ins_cred)
        self.partial_update_discussion_reply_helper(status.HTTP_200_OK)
        self.client.logout()
