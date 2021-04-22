import datetime
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from video.models import Video


class VideoViewSetTest(APITestCase):
    fixtures = [
        "users.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "chapters.test.yaml",
        "sections.test.yaml",
        "videos.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.
        """
        cls.ins_cred = {"email": "instructor@bodhitree.com", "password": "instructor"}
        cls.ta_cred = {"email": "ta@bodhitree.com", "password": "ta"}
        cls.stu_cred = {"email": "student@bodhitree.com", "password": "student"}

    def get_videos_helper(self):
        url = reverse("video:video-list-videos", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_videos(self):
        """
        Ensure we can get all Videos objects.
        """
        self.login(**self.ins_cred)
        self.get_videos_helper()
        self.logout()
        self.login(**self.ta_cred)
        self.get_videos_helper()
        self.logout()
        self.login(**self.stu_cred)
        self.get_videos_helper()
        self.logout()

    def get_videos_per_section_helper(self):
        url = reverse("video:video-list-videos-section", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_videos_section(self):
        """
        Ensure we can get all Videos objects per section .
        """
        self.login(**self.ins_cred)
        self.get_videos_per_section_helper()
        self.logout()
        self.login(**self.ta_cred)
        self.get_videos_per_section_helper()
        self.logout()
        self.login(**self.stu_cred)
        self.get_videos_per_section_helper()
        self.logout()

    def get_video_helper(self, video_id):
        url = reverse(
            "video:video-retrieve-video",
            kwargs={"pk": video_id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_video(self):
        """
        Ensure we can get one video object.
        """
        video_id = 5
        self.login(**self.ins_cred)
        self.get_video_helper(video_id)
        self.logout()
        self.login(**self.ta_cred)
        self.get_video_helper(video_id)
        self.logout()
        self.login(**self.stu_cred)
        self.get_video_helper(video_id)
        self.logout()

    def create_video_helper(self, title, video_duration, status_code):
        video_file_path = "main/test_data/video/sample-mp4-file.mp4"
        video_content = open(video_file_path, "rb").read()
        video_content = b"video_content"
        video = BytesIO(video_content)
        video.name = "video.mp4"
        doc_file_path = "main/test_data/video/eye-of-the-tiger-workout.pdf"
        doc_content = open(doc_file_path, "rb").read()
        doc_content = b"doc_content"
        doc = BytesIO(doc_content)
        data = {
            "chapter": 1,
            "section": "",
            "title": title,
            "video_file": video,
            "doc_file": doc,
            "video_duration": video_duration,
        }
        url = reverse("video:video-create-video", args=[1])
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)

    def test_create_video(self):
        """
        Ensure we can create a new 'Video' object
        """
        self.client.login(**self.ins_cred)
        self.create_video_helper(
            "Video3", datetime.timedelta(days=3), status.HTTP_201_CREATED
        )
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.create_video_helper(
            "Video4", datetime.timedelta(days=3), status.HTTP_201_CREATED
        )
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.create_video_helper(
            "Video5", datetime.timedelta(days=3), status.HTTP_403_FORBIDDEN
        )
        self.client.logout()

    def update_videos_helper(self, title, status_code):
        video_file_path = "main/test_data/video/sample-mp4-file.mp4"
        video_content = open(video_file_path, "rb").read()
        _file = SimpleUploadedFile("video.mp4", b"video_content")
        video1 = Video(
            title="Video77",
            chapter_id=1,
            video_file=_file,
            video_duration=datetime.timedelta(days=3),
        )
        video1.save()
        video_content = open(video_file_path, "rb").read()
        video_content = b"video_content"
        _file = SimpleUploadedFile("video.mp4", video_content)
        doc_file_path = "main/test_data/video/eye-of-the-tiger-workout.pdf"
        doc_content = open(doc_file_path, "rb").read()
        doc_content = b"doc_content"
        doc_file = SimpleUploadedFile("doc.pdf", doc_content)
        data = {
            "title": title,
            "chapter": 1,
            "video_file": _file,
            "doc_file": doc_file,
            "video_duration": datetime.timedelta(days=4),
        }
        url = reverse(("video:video-update-video"), kwargs={"pk": video1.id})
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)

    def test_update_videos(self):
        """
        Ensure we can update an existing Video object.
        """
        self.client.login(**self.ins_cred)
        self.update_videos_helper("video78", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.update_videos_helper("video79", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.update_videos_helper("video80", status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def partial_update_helper(self, title, status_code):
        video_file_path = "main/test_data/video/sample-mp4-file.mp4"
        video_content = open(video_file_path, "rb").read()
        video_content = b"video_content"
        _file = SimpleUploadedFile("video.mp4", video_content)
        video1 = Video(
            title="Video77",
            chapter_id=1,
            video_file=_file,
            video_duration=datetime.timedelta(days=3),
        )
        video1.save()
        data = {
            "title": title,
        }
        url = reverse(("video:video-update-video"), kwargs={"pk": video1.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)

    def test_partial_update_video(self):
        """
        Ensure we can partially update an existing Section object.
        """
        self.client.login(**self.ins_cred)
        self.partial_update_helper("Video78", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.partial_update_helper("Video79", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.partial_update_helper("Video80", status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def delete_video_helper(self, title, status_code):
        video_file_path = "main/test_data/video/sample-mp4-file.mp4"
        video_content = open(video_file_path, "rb").read()
        video_content = b"video_content"
        _file = SimpleUploadedFile("video.mp4", video_content)
        video1 = Video(
            title=title,
            chapter_id=1,
            video_file=_file,
            video_duration=datetime.timedelta(days=3),
        )
        video1.save()
        url = reverse(("video:video-delete-video"), kwargs={"pk": video1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)

    def test_delete_video(self):
        """
        Ensure we can delete an existing Video object.
        """
        self.client.login(**self.ins_cred)
        self.delete_video_helper("video98", status.HTTP_204_NO_CONTENT)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.delete_video_helper("video99", status.HTTP_204_NO_CONTENT)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.delete_video_helper("video100", status.HTTP_403_FORBIDDEN)
        self.client.logout()
