import datetime
from unittest import mock

from django.core.files import File
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from utils import credentials
from video.models import Video


ins_cred = credentials.TEST_INSTRUCTOR_CREDENTIALS
ta_cred = credentials.TEST_TA_CREDENTIALS
stu_cred = credentials.TEST_STUDENT_CREDENTIALS
stu_cred1 = credentials.TEST_STUDENT1_CREDENTIALS


class VideoViewSetTest(APITestCase):
    """Test for `VideoViewSet`."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
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

    def _create_video_helper(self, chapter_id, section_id, title, status_code):
        """Helper function `test_create_video()`.

        Args:
            chapter_id (int): Chapter id
            section_id (int): Section id
            title (str): Title of the video
            status_code (int): Expected status code of the API call
        """
        # Video mock file
        video_mock = mock.MagicMock(spec=File, name="FileMock")
        video_mock.name = "video.mp4"

        # Document mock file
        doc_mock = mock.MagicMock(spec=File, name="FileMock")
        doc_mock.name = "doc.pdf"

        data = {
            "chapter": chapter_id,
            "section": section_id,
            "title": title,
            "description": "This is the video description",
            "video_file": video_mock,
            "doc_file": doc_mock,
            "video_duration": datetime.timedelta(minutes=3),
        }
        url = reverse("video:video-create-video")

        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            if chapter_id:
                self.assertEqual(response_data["chapter"], data["chapter"])
            if section_id:
                self.assertEqual(response_data["section"], data["section"])
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    @mock.patch("django.core.files.storage.FileSystemStorage.save")
    def test_create_video(self, mock_save):
        """Test: create a video.

        Args:
            mock_save (MagicMock): Mock object for django file storage
        """
        mock_save.return_value = "video.mp4"
        chapter_id = 1
        section_id = ""

        # Created by instructor (in chapter)
        self.login(**ins_cred)
        self._create_video_helper(
            "Video 1", status.HTTP_201_CREATED, chapter_id, section_id
        )
        self.logout()

        # Created by ta (in chapter)
        self.login(**ta_cred)
        self._create_video_helper(
            "Video 2", status.HTTP_201_CREATED, chapter_id, section_id
        )
        self.logout()

        # Created by instructor (in section)
        chapter_id = ""
        section_id = 1
        self.login(**ins_cred)
        self._create_video_helper(
            "Video 1", status.HTTP_201_CREATED, chapter_id, section_id
        )
        self.logout()

        # Created by ta (in section)
        self.login(**ins_cred)
        self._create_video_helper(
            "Video 2", status.HTTP_201_CREATED, chapter_id, section_id
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_video_helper(
            "", status.HTTP_400_BAD_REQUEST, chapter_id, section_id
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to  both the section and chapter is provided
        chapter_id = 1
        self.login(**ins_cred)
        self._create_video_helper(
            "Video 3", status.HTTP_400_BAD_REQUEST, chapter_id, section_id
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to  none of the section and chapter is provided
        chapter_id = ""
        section_id = ""
        self.login(**ins_cred)
        self._create_video_helper(
            "Video 4", status.HTTP_400_BAD_REQUEST, chapter_id, section_id
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        chapter_id = 1
        self._create_video_helper(
            "Video 5", status.HTTP_401_UNAUTHORIZED, chapter_id, section_id
        )

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._create_video_helper(
            "Video 6", status.HTTP_403_FORBIDDEN, chapter_id, section_id
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to chapter does not exist
        chapter_id = 100
        self.login(**ins_cred)
        self._create_video_helper(
            "Video 7", status.HTTP_404_NOT_FOUND, chapter_id, section_id
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to section does not exist
        chapter_id = ""
        section_id = 100
        self.login(**ins_cred)
        self._create_video_helper(
            "Video 8", status.HTTP_404_NOT_FOUND, chapter_id, section_id
        )
        self.logout()

    def _list_chapter_videos_helper(self, chapter_id, status_code):
        """Helper function for `test_list_chapter_videos()`.

        Args:
            chapter_id (int): Chapter id
            status_code (int): Expected status code of the API call
        """
        url = reverse("video:video-list-chapter-videos", args=[chapter_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            no_of_videos = Video.objects.filter(chapter_id=chapter_id).count()
            self.assertEqual(len(response.data), no_of_videos)

    def test_list_chapter_videos(self):
        """Test: list all chapter videos."""
        chapter_id = 1

        # List by instructor
        self.login(**ins_cred)
        self._list_chapter_videos_helper(chapter_id, status.HTTP_200_OK)
        self.logout()

        # List by ta
        self.login(**ta_cred)
        self._list_chapter_videos_helper(chapter_id, status.HTTP_200_OK)
        self.logout()

        # List by student
        self.login(**stu_cred)
        self._list_chapter_videos_helper(chapter_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permisison class
        self._list_chapter_videos_helper(chapter_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        chapter_id = 3
        self.login(**stu_cred)
        self._list_chapter_videos_helper(chapter_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the chapter does not exist
        chapter_id = 100
        self.login(**stu_cred)
        self._list_chapter_videos_helper(chapter_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _list_section_videos_helper(self, section_id, status_code):
        """Helper function for `test_list_section_videos()`.

        Args:
            section_id (int): Section id
            status_code (int): Expected status code of the API call
        """
        url = reverse("video:video-list-section-videos", args=[section_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            no_of_videos = Video.objects.filter(section_id=section_id).count()
            self.assertEqual(len(response.data), no_of_videos)

    def test_list_section_videos(self):
        """Test: list all section videos."""
        section_id = 1

        # List by instructor
        self.login(**ins_cred)
        self._list_section_videos_helper(section_id, status.HTTP_200_OK)
        self.logout()

        # List by ta
        self.login(**ta_cred)
        self._list_section_videos_helper(section_id, status.HTTP_200_OK)
        self.logout()

        # List by student
        self.login(**stu_cred)
        self._list_section_videos_helper(section_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permisison class
        self._list_section_videos_helper(section_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        section_id = 3
        self.login(**stu_cred)
        self._list_section_videos_helper(section_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the chapter does not exist
        section_id = 100
        self.login(**stu_cred)
        self._list_section_videos_helper(section_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _retrieve_video_helper(self, video_id, status_code):
        """Helper function for `test_retrieve_video()`.

        Args:
            video_id (int): Video id
            status_code (int): Expected status code of the API call
        """

        url = reverse("video:video-retrieve-video", args=[video_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], video_id)

    def test_retrieve_video(self):
        """Test to check: retrieve the video."""
        video_id = 1

        # Retrieve by instructor
        self.login(**ins_cred)
        self._retrieve_video_helper(video_id, status.HTTP_200_OK)
        self.logout()

        # Retrieve by ta
        self.login(**ta_cred)
        self._retrieve_video_helper(video_id, status.HTTP_200_OK)
        self.logout()

        # Retrieve by student
        self.login(**stu_cred)
        self._retrieve_video_helper(video_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permisison class
        self._retrieve_video_helper(video_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permisison class
        self.login(**stu_cred1)
        self._retrieve_video_helper(video_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `is_object()` method
        video_id = 100
        self.login(**stu_cred)
        self._retrieve_video_helper(video_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _update_video_helper(self, video, title, status_code, method):
        """Helper function to test update video functionality.

        Args:
            video (Video): `Video` model object
            title (str): Title of the video
            status_code (int): Expected status code of the API call
            method (str): HTTP method ("PUT" or "PATCH")
        """
        # Video mock file
        video_mock = mock.MagicMock(spec=File, name="FileMock")
        video_mock.name = "video.mp4"

        # Document mock file
        doc_mock = mock.MagicMock(spec=File, name="FileMock")
        doc_mock.name = "doc.pdf"

        data = {
            "title": title,
            "description": "This is the video description",
            "video_file": video_mock,
            "doc_file": doc_mock,
            "video_duration": datetime.timedelta(minutes=3),
        }
        if video.chapter_id:
            data["chapter"] = video.chapter_id
        elif video.section_id:
            data["section"] = video.section_id
        url = reverse(("video:video-update-video"), args=[video.id])

        if method == "PUT":
            response = self.client.put(url, data, format="multipart")
        else:
            response = self.client.patch(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])
            if video.chapter_id:
                self.assertEqual(response_data["chapter"], data["chapter"])
            elif video.section_id:
                self.assertEqual(response_data["section"], data["section"])

    def _put_or_patch(self, mock_save, method):
        """Helper function for deciding full(PUT) or partial(PATCH) update.

        Args:
            mock_save (MagicMock): Mock object for django file storage
            method (str): HTTP method ("PUT" or "PATCH")
        """
        mock_save.return_value = "video.mp4"

        # Video mock file
        video_mock = mock.MagicMock(spec=File, name="FileMock")
        video_mock.name = "video.mp4"

        # Document mock file
        doc_mock = mock.MagicMock(spec=File, name="FileMock")
        doc_mock.name = "doc.pdf"

        chapter_id = 1
        section_id = 1
        video_in_ch = Video.objects.create(
            title="Video in chapter",
            chapter_id=chapter_id,
            video_file=video_mock,
            video_duration=datetime.timedelta(minutes=3),
        )
        video_in_sec = Video.objects.create(
            title="Video in section",
            section_id=section_id,
            video_file=video_mock,
            video_duration=datetime.timedelta(minutes=3),
        )

        # Update by instructor (in chapter)
        self.login(**ins_cred)
        self._update_video_helper(video_in_ch, "Video 1", status.HTTP_200_OK, method)
        self.logout()

        # Update by ta (in chapter)
        self.login(**ta_cred)
        self._update_video_helper(video_in_ch, "Video 2", status.HTTP_200_OK, method)
        self.logout()

        # Update by instructor (in section)
        self.login(**ins_cred)
        self._update_video_helper(video_in_sec, "Video 1", status.HTTP_200_OK, method)
        self.logout()

        # Update by ta (in section)
        self.login(**ta_cred)
        self._update_video_helper(video_in_sec, "Video 2", status.HTTP_200_OK, method)
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._update_video_helper(video_in_sec, "", status.HTTP_400_BAD_REQUEST, method)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._update_video_helper(
            video_in_sec, "Video 3", status.HTTP_401_UNAUTHORIZED, method
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._update_video_helper(
            video_in_ch, "Video 4", status.HTTP_403_FORBIDDEN, method
        )
        self.logout()

    @mock.patch("django.core.files.storage.FileSystemStorage.save")
    def test_update_video(self, mock_save):
        """Test: update the video.

        Args:
            mock_save (MagicMock): Mock object for django file storage
        """
        self._put_or_patch(mock_save, "PUT")

    @mock.patch("django.core.files.storage.FileSystemStorage.save")
    def test_partial_update_video(self, mock_save):
        """Test: partial update the video.

        Args:
            mock_save (MagicMock): Mock object for django file storage
        """
        self._put_or_patch(mock_save, "PATCH")

    def _delete_video_helper(self, title, status_code):
        """Helper function for `test_delete_video()`.

        Args:
            title (str): Title of the video
            status_code (int): Expected status code of the API call
        """
        # Video mock file
        video_mock = mock.MagicMock(spec=File, name="FileMock")
        video_mock.name = "video.mp4"

        # Document mock file
        doc_mock = mock.MagicMock(spec=File, name="FileMock")
        doc_mock.name = "doc.pdf"

        chapter_id = 1
        section_id = 1
        video_in_ch = Video.objects.create(
            title=title,
            chapter_id=chapter_id,
            video_file=video_mock,
            video_duration=datetime.timedelta(minutes=3),
        )
        video_in_sec = Video.objects.create(
            title=title,
            section_id=section_id,
            video_file=video_mock,
            video_duration=datetime.timedelta(minutes=3),
        )
        for video in [video_in_ch, video_in_sec]:
            url = reverse(("video:video-delete-video"), args=[video.id])
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status_code)
            if status_code == status.HTTP_204_NO_CONTENT:
                self.assertEqual(Video.objects.filter(id=video.id).count(), 0)

    @mock.patch("django.core.files.storage.FileSystemStorage.save")
    def test_delete_video(self, mock_save):
        """Test: delete the video.

        Args:
            mock_save (MagicMock): Mock object for django file storage
        """
        mock_save.return_value = "video.mp4"

        # Deleted by instructor
        self.login(**ins_cred)
        self._delete_video_helper("Video 1", status.HTTP_204_NO_CONTENT)
        self.logout()

        # Deleted by ta
        self.login(**ta_cred)
        self._delete_video_helper("Video 2", status.HTTP_204_NO_CONTENT)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permisison class
        self._delete_video_helper("Video 3", status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permisison class
        self.login(**stu_cred)
        self._delete_video_helper("Video 4", status.HTTP_403_FORBIDDEN)
        self.logout()
