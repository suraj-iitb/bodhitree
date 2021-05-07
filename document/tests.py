from unittest import mock

from django.core.files import File
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from document.models import Document
from utils import credentials


ins_cred = credentials.TEST_INSTRUCTOR_CREDENTIALS
ta_cred = credentials.TEST_TA_CREDENTIALS
stu_cred = credentials.TEST_STUDENT_CREDENTIALS


class DocumentViewSetTest(APITestCase):
    """Test for `DocumentViewSet`."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "chapters.test.yaml",
        "sections.test.yaml",
        "documents.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_document_helper(self, chapter_id, section_id, title, status_code):
        """Helper function `test_create_document()`.

        Args:
            chapter_id (int): Chapter id
            section_id (int): Section id
            title (str): Title of the document
            status_code (int): Expected status code of the API call
        """
        # Document mock file
        doc_mock = mock.MagicMock(spec=File, name="FileMock")
        doc_mock.name = "doc.pdf"

        data = {
            "chapter": chapter_id,
            "section": section_id,
            "title": title,
            "description": "This is the document description",
            "doc_file": doc_mock,
        }
        url = reverse("document:document-create-document")

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
    def test_create_document(self, mock_save):
        """Test: create a document.

        Args:
            mock_save (MagicMock): Mock object for django file storage
        """
        mock_save.return_value = "doc.pdf"
        chapter_id = 1
        section_id = ""

        # Created by instructor (in chapter)
        self.login(**ins_cred)
        self._create_document_helper(
            chapter_id, section_id, "Document 1", status.HTTP_201_CREATED
        )
        self.logout()

        # Created by ta (in chapter)
        self.login(**ta_cred)
        self._create_document_helper(
            chapter_id, section_id, "Document 2", status.HTTP_201_CREATED
        )
        self.logout()

        # Created by instructor (in section)
        chapter_id = ""
        section_id = 1
        self.login(**ins_cred)
        self._create_document_helper(
            chapter_id, section_id, "Document 1", status.HTTP_201_CREATED
        )
        self.logout()

        # Created by ta (in section)
        self.login(**ins_cred)
        self._create_document_helper(
            chapter_id, section_id, "Document 2", status.HTTP_201_CREATED
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_document_helper(
            chapter_id, section_id, "", status.HTTP_400_BAD_REQUEST
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to  both the section and chapter is provided
        chapter_id = 1
        self.login(**ins_cred)
        self._create_document_helper(
            chapter_id, section_id, "Document 3", status.HTTP_400_BAD_REQUEST
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to  none of the section and chapter is provided
        chapter_id = ""
        section_id = ""
        self.login(**ins_cred)
        self._create_document_helper(
            chapter_id, section_id, "Document 4", status.HTTP_400_BAD_REQUEST
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        chapter_id = 1
        self._create_document_helper(
            chapter_id, section_id, "Document 5", status.HTTP_401_UNAUTHORIZED
        )

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._create_document_helper(
            chapter_id, section_id, "Document 6", status.HTTP_403_FORBIDDEN
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to chapter does not exist
        chapter_id = 100
        self.login(**ins_cred)
        self._create_document_helper(
            chapter_id, section_id, "Document 7", status.HTTP_404_NOT_FOUND
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to section does not exist
        chapter_id = ""
        section_id = 100
        self.login(**ins_cred)
        self._create_document_helper(
            chapter_id, section_id, "Document 8", status.HTTP_404_NOT_FOUND
        )
        self.logout()

    def _list_chapter_documents_helper(self, chapter_id, status_code):
        """Helper function for `test_list_chapter_documents()`.

        Args:
            chapter_id (int): Chapter id
            status_code (int): Expected status code of the API call
        """
        url = reverse("document:document-list-chapter-documents", args=[chapter_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            no_of_documents = Document.objects.filter(chapter_id=chapter_id).count()
            self.assertEqual(len(response.data), no_of_documents)

    def test_list_chapter_documents(self):
        """Test: list all chapter documents."""
        chapter_id = 1

        # Listed by instructor
        self.login(**ins_cred)
        self._list_chapter_documents_helper(chapter_id, status.HTTP_200_OK)
        self.logout()

        # Listed by ta
        self.login(**ta_cred)
        self._list_chapter_documents_helper(chapter_id, status.HTTP_200_OK)
        self.logout()

        # Listed by student
        self.login(**stu_cred)
        self._list_chapter_documents_helper(chapter_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permisison class
        self._list_chapter_documents_helper(chapter_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        chapter_id = 3
        self.login(**stu_cred)
        self._list_chapter_documents_helper(chapter_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the chapter does not exist
        chapter_id = 100
        self.login(**stu_cred)
        self._list_chapter_documents_helper(chapter_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _list_section_documents_helper(self, section_id, status_code):
        """Helper function for `test_list_section_documents()`.

        Args:
            section_id (int): Section id
            status_code (int): Expected status code of the API call
        """
        url = reverse("document:document-list-section-documents", args=[section_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            no_of_documents = Document.objects.filter(section_id=section_id).count()
            self.assertEqual(len(response.data), no_of_documents)

    def test_list_section_documents(self):
        """Test: list all section documents."""
        section_id = 1

        # Listed by instructor
        self.login(**ins_cred)
        self._list_section_documents_helper(section_id, status.HTTP_200_OK)
        self.logout()

        # Listed by ta
        self.login(**ta_cred)
        self._list_section_documents_helper(section_id, status.HTTP_200_OK)
        self.logout()

        # Listed by student
        self.login(**stu_cred)
        self._list_section_documents_helper(section_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permisison class
        self._list_section_documents_helper(section_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        section_id = 3
        self.login(**stu_cred)
        self._list_section_documents_helper(section_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the chapter does not exist
        section_id = 100
        self.login(**stu_cred)
        self._list_section_documents_helper(section_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _retrieve_document_helper(self, document_id, status_code):
        """Helper function for `test_retrieve_document()`.

        Args:
            document_id (int): Document id
            status_code (int): Expected status code of the API call
        """
        url = reverse("document:document-retrieve-document", args=[document_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], document_id)

    def test_retrieve_document(self):
        """Test: retrieve the document."""
        document_id = 1

        # Retrieved by instructor
        self.login(**ins_cred)
        self._retrieve_document_helper(document_id, status.HTTP_200_OK)
        self.logout()

        # Retrieved by ta
        self.login(**ta_cred)
        self._retrieve_document_helper(document_id, status.HTTP_200_OK)
        self.logout()

        # Retrieved by student
        self.login(**stu_cred)
        self._retrieve_document_helper(document_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permisison class
        self._retrieve_document_helper(document_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permisison class
        document_id = 4
        self.login(**stu_cred)
        self._retrieve_document_helper(document_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `is_object()` method
        document_id = 100
        self.login(**stu_cred)
        self._retrieve_document_helper(document_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _update_document_helper(self, document, title, status_code, method):
        """Helper function for `test_update_document()` & `test_partial_update_document()`.

        Args:
            document (Document): `Document` model object
            title (str): Title of the document
            status_code (int): Expected status code of the API call
            method (str): HTTP method ("PUT" or "PATCH")
        """
        # Document mock file
        doc_mock = mock.MagicMock(spec=File, name="FileMock")
        doc_mock.name = "doc.pdf"

        data = {
            "title": title,
            "description": "This is the documet description",
            "doc_file": doc_mock,
        }
        if document.chapter_id:
            data["chapter"] = document.chapter_id
        elif document.section_id:
            data["section"] = document.section_id

        url = reverse(("document:document-update-document"), args=[document.id])
        if method == "PUT":
            response = self.client.put(url, data, format="multipart")
        else:
            response = self.client.patch(url, data, format="multipart")

        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])
            if document.chapter_id:
                self.assertEqual(response_data["chapter"], data["chapter"])
            elif document.section_id:
                self.assertEqual(response_data["section"], data["section"])

    def _put_or_patch(self, mock_save, method):
        """Helper function for deciding full(PUT) or partial(PATCH) update.

        Args:
            mock_save (MagicMock): Mock object for django file storage
            method (str): HTTP method ("PUT" or "PATCH")
        """
        mock_save.return_value = "doc.pdf"

        # Document mock file
        doc_mock = mock.MagicMock(spec=File, name="FileMock")
        doc_mock.name = "doc.pdf"

        chapter_id = 1
        section_id = 1
        document_in_ch = Document.objects.create(
            title="Document in chapter",
            chapter_id=chapter_id,
            doc_file=doc_mock,
        )
        document_in_sec = Document.objects.create(
            title="Document in section",
            section_id=section_id,
            doc_file=doc_mock,
        )

        # Updated by instructor (in chapter)
        self.login(**ins_cred)
        self._update_document_helper(
            document_in_ch, "Document 1", status.HTTP_200_OK, method
        )
        self.logout()

        # Updated by ta (in chapter)
        self.login(**ta_cred)
        self._update_document_helper(
            document_in_ch, "Document 2", status.HTTP_200_OK, method
        )
        self.logout()

        # Updated by instructor (in section)
        self.login(**ins_cred)
        self._update_document_helper(
            document_in_sec, "Document 1", status.HTTP_200_OK, method
        )
        self.logout()

        # Updated by ta (in section)
        self.login(**ta_cred)
        self._update_document_helper(
            document_in_sec, "Document 2", status.HTTP_200_OK, method
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._update_document_helper(
            document_in_sec, "", status.HTTP_400_BAD_REQUEST, method
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._update_document_helper(
            document_in_sec, "Document 3", status.HTTP_401_UNAUTHORIZED, method
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._update_document_helper(
            document_in_ch, "Document 4", status.HTTP_403_FORBIDDEN, method
        )
        self.logout()

    @mock.patch("django.core.files.storage.FileSystemStorage.save")
    def test_update_document(self, mock_save):
        """Test: update the document.

        Args:
            mock_save (MagicMock): Mock object for django file storage
        """
        self._put_or_patch(mock_save, "PUT")

    @mock.patch("django.core.files.storage.FileSystemStorage.save")
    def test_partial_update_document(self, mock_save):
        """Test: partial update the document.

        Args:
            mock_save (MagicMock): Mock object for django file storage
        """
        self._put_or_patch(mock_save, "PATCH")

    def _delete_document_helper(self, title, status_code):
        """Helper function for `test_delete_document()`.

        Args:
            title (str): Title of the document
            status_code (int): Expected status code of the API call
        """
        # Document mock file
        doc_mock = mock.MagicMock(spec=File, name="FileMock")
        doc_mock.name = "doc.pdf"

        chapter_id = 1
        section_id = 1
        document_in_ch = Document.objects.create(
            title=title,
            chapter_id=chapter_id,
            doc_file=doc_mock,
        )
        document_in_sec = Document.objects.create(
            title=title,
            section_id=section_id,
            doc_file=doc_mock,
        )

        for document in [document_in_ch, document_in_sec]:
            url = reverse("document:document-delete-document", args=[document.id])
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status_code)
            if status_code == status.HTTP_204_NO_CONTENT:
                self.assertEqual(Document.objects.filter(id=document.id).count(), 0)

    def test_delete_document(self):
        """Test: delete the document."""
        # Deleted by instructor
        self.login(**ins_cred)
        self._delete_document_helper("Document 1", status.HTTP_204_NO_CONTENT)
        self.logout()

        # Deleted by ta
        self.login(**ta_cred)
        self._delete_document_helper("Document 2", status.HTTP_204_NO_CONTENT)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permisison class
        self._delete_document_helper("Document 3", status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permisison class
        self.login(**stu_cred)
        self._delete_document_helper("Document 4", status.HTTP_403_FORBIDDEN)
        self.logout()
