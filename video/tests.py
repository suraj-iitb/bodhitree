import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from video.models import Video


# These users are created by django fixtures
# instructor has user id 1
ins_cred = {"email": "instructor@bodhitree.com", "password": "instructor"}
# ta has user id 2
ta_cred = {"email": "ta@bodhitree.com", "password": "ta"}
# student has user id 3
stu_cred = {"email": "student@bodhitree.com", "password": "student"}


class VideoViewSetTest(APITestCase):
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

    def _list_chapter_videos_helper(self):
        """Helper function to test list all chapter videos functionality."""
        chapter_id = 1
        url = reverse("video:video-list-chapter-videos", args=[chapter_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        no_of_videos = Video.objects.filter(chapter_id=chapter_id).count()
        self.assertEqual(len(response.data), no_of_videos)

    def test_list_chapter_videos(self):
        """Test to check: list all chapter videos."""
        self.login(**ins_cred)
        self._list_chapter_videos_helper()
        self.logout()
        self.login(**ta_cred)
        self._list_chapter_videos_helper()
        self.logout()
        self.login(**stu_cred)
        self._list_chapter_videos_helper()
        self.logout()

    def _list_section_videos_helper(self):
        """Helper function to test list all chapter videos functionality."""
        section_id = 1
        url = reverse("video:video-list-section-videos", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        no_of_videos = Video.objects.filter(section_id=section_id).count()
        self.assertEqual(len(response.data), no_of_videos)

    def test_list_section_videos(self):
        """Test to check: list all section videos."""
        self.login(**ins_cred)
        self._list_section_videos_helper()
        self.logout()
        self.login(**ta_cred)
        self._list_section_videos_helper()
        self.logout()
        self.login(**stu_cred)
        self._list_section_videos_helper()
        self.logout()

    def _retrieve_video_helper(self):
        """Helper function to test retrieve the video functionality."""
        video_id = 1
        url = reverse("video:video-retrieve-video", args=[video_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], video_id)

    def test_retrieve_video(self):
        """Test to check: retrieve the video."""
        self.login(**ins_cred)
        self._retrieve_video_helper()
        self.logout()
        self.login(**ta_cred)
        self._retrieve_video_helper()
        self.logout()
        self.login(**stu_cred)
        self._retrieve_video_helper()
        self.logout()

    def _get_in_memory_file(self, input_file_path, output_file_name):
        file_content = open(input_file_path, "rb").read()
        file_content = b"file_content"
        in_memory_file = SimpleUploadedFile(output_file_name, file_content)
        return in_memory_file

    def _create_video_helper(self, title, status_code):
        """Helper function to test create video functionality.

        Args:
            title (str): title of the video
            status_code (int): expected status code of the API call
        """
        chapter_id = 1
        # Video file
        video_file_path = "main/test_data/video/sample-mp4-file.mp4"
        output_file_name = "video.mp4"
        in_memory_video_file = self._get_in_memory_file(
            video_file_path, output_file_name
        )

        # Accompanied doc file to video
        doc_file_path = "main/test_data/video/eye-of-the-tiger-workout.pdf"
        output_file_name = "doc.pdf"
        in_memory_doc_file = self._get_in_memory_file(doc_file_path, output_file_name)

        data = {
            "chapter": chapter_id,
            "section": "",
            "title": title,
            "video_file": in_memory_video_file,
            "doc_file": in_memory_doc_file,
            "video_duration": datetime.timedelta(minutes=3),
            "description": "this is the video description",
        }
        url = reverse("video:video-create-video")
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["chapter"], data["chapter"])
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def test_create_video(self):
        """Test to check: create a video."""
        self.login(**ins_cred)
        self._create_video_helper("Video 3", status.HTTP_201_CREATED)
        self.logout()
        self.login(**ta_cred)
        self._create_video_helper("Video 4", status.HTTP_201_CREATED)
        self.logout()
        self.login(**stu_cred)
        self._create_video_helper("Video 5", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _update_video_helper(self, title, status_code):
        """Helper function to test update video functionality.

        Args:
            title (str): title of the course
            status_code (int): expected status code of the API call
        """
        chapter_id = 1
        # Video file
        video_file_path = "main/test_data/video/sample-mp4-file.mp4"
        output_file_name = "video.mp4"
        in_memory_video_file = self._get_in_memory_file(
            video_file_path, output_file_name
        )

        video = Video(
            title="Video 6",
            chapter_id=chapter_id,
            video_file=in_memory_video_file,
            video_duration=datetime.timedelta(minutes=3),
        )
        video.save()

        # Video file
        in_memory_video_file = self._get_in_memory_file(
            video_file_path, output_file_name
        )
        # Accompanied doc file to video
        doc_file_path = "main/test_data/video/eye-of-the-tiger-workout.pdf"
        output_file_name = "doc.pdf"
        in_memory_doc_file = self._get_in_memory_file(doc_file_path, output_file_name)

        data = {
            "title": title,
            "chapter": chapter_id,
            "video_file": in_memory_video_file,
            "doc_file": in_memory_doc_file,
            "video_duration": datetime.timedelta(minutes=3),
            "description": "This is the video description",
        }

        url = reverse(("video:video-update-video"), args=[video.id])
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])
            self.assertEqual(response_data["chapter"], data["chapter"])

    def test_update_videos(self):
        """Test to check: update a video."""
        self.login(**ins_cred)
        self._update_video_helper("Video 7", status.HTTP_200_OK)
        self.logout()
        self.login(**ta_cred)
        self._update_video_helper("Video 8", status.HTTP_200_OK)
        self.logout()
        self.login(**stu_cred)
        self._update_video_helper("Video 9", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _partial_update_video_helper(self, title, status_code):
        """Helper function to test partial update video functionality.

        Args:
            title (str): title of the course
            status_code (int): expected status code of the API call
        """
        chapter_id = 1
        # Video file
        video_file_path = "main/test_data/video/sample-mp4-file.mp4"
        output_file_name = "video.mp4"
        in_memory_video_file = self._get_in_memory_file(
            video_file_path, output_file_name
        )

        video = Video(
            title="Video 6",
            chapter_id=chapter_id,
            video_file=in_memory_video_file,
            video_duration=datetime.timedelta(minutes=3),
        )
        video.save()

        data = {
            "title": title,
            "description": "This is the video description",
        }

        url = reverse(("video:video-update-video"), args=[video.id])
        response = self.client.patch(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def test_partial_update_videos(self):
        """Test to check: update a video."""
        self.login(**ins_cred)
        self._partial_update_video_helper("Video 10", status.HTTP_200_OK)
        self.logout()
        self.login(**ta_cred)
        self._partial_update_video_helper("Video 11", status.HTTP_200_OK)
        self.logout()
        self.login(**stu_cred)
        self._partial_update_video_helper("Video 12", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _delete_video_helper(self, title, status_code):
        """Helper function to test delete video functionality

        Args:
            title (str): title of the course
            status_code (int): expected status code of the API call
        """
        # Video file
        chapter_id = 1
        video_file_path = "main/test_data/video/sample-mp4-file.mp4"
        output_file_name = "video.mp4"
        in_memory_video_file = self._get_in_memory_file(
            video_file_path, output_file_name
        )

        video = Video(
            title="Video 6",
            chapter_id=chapter_id,
            video_file=in_memory_video_file,
            video_duration=datetime.timedelta(minutes=3),
        )
        video.save()
        url = reverse(("video:video-delete-video"), args=[video.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Video.objects.filter(id=video.id).count(), 0)

    def test_delete_video(self):
        """Test to check: delete the video."""
        self.login(**ins_cred)
        self._delete_video_helper("Video 13", status.HTTP_204_NO_CONTENT)
        self.logout()
        self.login(**ta_cred)
        self._delete_video_helper("Video 14", status.HTTP_204_NO_CONTENT)
        self.logout()
        self.login(**stu_cred)
        self._delete_video_helper("Video 14", status.HTTP_403_FORBIDDEN)
        self.logout()
