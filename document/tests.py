from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from document.models import Document


# These users are created by django fixtures
# instructor has user id 1
ins_cred = {"email": "instructor@bodhitree.com", "password": "instructor"}
# ta has user id 2
ta_cred = {"email": "ta@bodhitree.com", "password": "ta"}
# student has user id 3
stu_cred = {"email": "student@bodhitree.com", "password": "student"}


class DocumentViewSetTest(APITestCase):
    """Test for DocumentViewSet"""

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

    def _list_chapter_documents_helper(self):
        """Helper function to test list all chapter documents functionality."""
        chapter_id = 1
        url = reverse("document:document-list-chapter-documents", args=[chapter_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        no_of_documents = Document.objects.filter(chapter_id=chapter_id).count()
        self.assertEqual(len(response.data), no_of_documents)

    def test_list_chapter_documents(self):
        """Test to check: list all chapter videos."""
        self.login(**ins_cred)
        self._list_chapter_documents_helper()
        self.logout()
        self.login(**ta_cred)
        self._list_chapter_documents_helper()
        self.logout()
        self.login(**stu_cred)
        self._list_chapter_documents_helper()
        self.logout()

    def _list_section_documents_helper(self):
        """Helper function to test list all chapter documents functionality."""
        section_id = 1
        url = reverse("document:document-list-section-documents", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        no_of_documents = Document.objects.filter(section_id=section_id).count()
        self.assertEqual(len(response.data), no_of_documents)

    def test_list_section_documents(self):
        """Test to check: list all section videos."""
        self.login(**ins_cred)
        self._list_section_documents_helper()
        self.logout()
        self.login(**ta_cred)
        self._list_section_documents_helper()
        self.logout()
        self.login(**stu_cred)
        self._list_section_documents_helper()
        self.logout()

    def _retrieve_document_helper(self):
        """Helper function to test retrieve the document functionality."""
        document_id = 1
        url = reverse("document:document-retrieve-document", args=[document_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], document_id)

    def test_retrieve_document(self):
        """Test to check: retrieve the document."""
        self.login(**ins_cred)
        self._retrieve_document_helper()
        self.logout()
        self.login(**ta_cred)
        self._retrieve_document_helper()
        self.logout()
        self.login(**stu_cred)
        self._retrieve_document_helper()
        self.logout()

    def _get_in_memory_file(self, input_file_path, output_file_name):
        file_content = open(input_file_path, "rb").read()
        file_content = b"file_content"
        in_memory_file = SimpleUploadedFile(output_file_name, file_content)
        return in_memory_file

    def _create_document_helper(self, title, status_code):
        """Helper function to test create document functionality.

        Args:
            title (str): title of the document
            status_code (int): expected status code of the API call
        """
        chapter_id = 1
        # Document file
        doc_file_path = "main/test_data/doc/eye-of-the-tiger-workout.pdf"
        output_file_name = "doc.pdf"
        in_memory_doc_file = self._get_in_memory_file(doc_file_path, output_file_name)

        data = {
            "chapter": chapter_id,
            "section": "",
            "title": title,
            "doc_file": in_memory_doc_file,
            "description": "this is the document description",
        }
        url = reverse("document:document-create-document")
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["chapter"], data["chapter"])
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def test_create_document(self):
        """Test to check: create a document."""
        self.login(**ins_cred)
        self._create_document_helper("Document 3", status.HTTP_201_CREATED)
        self.logout()
        self.login(**ta_cred)
        self._create_document_helper("Document 4", status.HTTP_201_CREATED)
        self.logout()
        self.login(**stu_cred)
        self._create_document_helper("Document 5", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _update_document_helper(self, title, status_code):
        """Helper function to test update document functionality.

        Args:
            title (str): title of the document
            status_code (int): expected status code of the API call
        """
        chapter_id = 1
        # Document file
        doc_file_path = "main/test_data/doc/eye-of-the-tiger-workout.pdf"
        output_file_name = "doc.pdf"
        in_memory_doc_file = self._get_in_memory_file(doc_file_path, output_file_name)

        document = Document(
            title="Document 6",
            chapter_id=chapter_id,
            doc_file=in_memory_doc_file,
        )
        document.save()

        # Document file
        in_memory_doc_file = self._get_in_memory_file(doc_file_path, output_file_name)

        data = {
            "title": title,
            "chapter": chapter_id,
            "doc_file": in_memory_doc_file,
            "description": "This is the video description",
        }

        url = reverse(("document:document-update-document"), args=[document.id])
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])
            self.assertEqual(response_data["chapter"], data["chapter"])

    def test_update_document(self):
        """Test to check: update a document."""
        self.login(**ins_cred)
        self._update_document_helper("Document 7", status.HTTP_200_OK)
        self.logout()
        self.login(**ta_cred)
        self._update_document_helper("Document 8", status.HTTP_200_OK)
        self.logout()
        self.login(**stu_cred)
        self._update_document_helper("Document 9", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _partial_update_document_helper(self, title, status_code):
        """Helper function to test partial update document functionality.

        Args:
            title (str): title of the document
            status_code (int): expected status code of the API call
        """
        chapter_id = 1
        # Document file
        doc_file_path = "main/test_data/doc/eye-of-the-tiger-workout.pdf"
        output_file_name = "doc.pdf"
        in_memory_doc_file = self._get_in_memory_file(doc_file_path, output_file_name)

        document = Document(
            title="Document 6",
            chapter_id=chapter_id,
            doc_file=in_memory_doc_file,
        )
        document.save()

        data = {
            "title": title,
            "description": "This is the video description",
        }

        url = reverse(("document:document-update-document"), args=[document.id])
        response = self.client.patch(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def test_partial_update_document(self):
        """Test to check: update a document."""
        self.login(**ins_cred)
        self._partial_update_document_helper("Document 10", status.HTTP_200_OK)
        self.logout()
        self.login(**ta_cred)
        self._partial_update_document_helper("Document 11", status.HTTP_200_OK)
        self.logout()
        self.login(**stu_cred)
        self._partial_update_document_helper("Document 12", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _delete_document_helper(self, title, status_code):
        """Helper function to test delete document functionality

        Args:
            title (str): title of the document
            status_code (int): expected status code of the API call
        """
        # Video file
        chapter_id = 1
        doc_file_path = "main/test_data/doc/eye-of-the-tiger-workout.pdf"
        output_file_name = "doc.pdf"
        in_memory_doc_file = self._get_in_memory_file(doc_file_path, output_file_name)

        document = Document(
            title="Document 6",
            chapter_id=chapter_id,
            doc_file=in_memory_doc_file,
        )
        document.save()

        url = reverse("document:document-delete-document", args=[document.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Document.objects.filter(id=document.id).count(), 0)

    def test_delete_document(self):
        """Test to check: delete the document."""
        self.login(**ins_cred)
        self._delete_document_helper("Document 13", status.HTTP_204_NO_CONTENT)
        self.logout()
        self.login(**ta_cred)
        self._delete_document_helper("Document 14", status.HTTP_204_NO_CONTENT)
        self.logout()
        self.login(**stu_cred)
        self._delete_document_helper("Document 15", status.HTTP_403_FORBIDDEN)
        self.logout()
