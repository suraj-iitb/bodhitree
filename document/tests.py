from io import BytesIO

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from document.models import Document


class DocumentViewSetTest(APITestCase):
    fixtures = [
        "users.test.yaml",
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

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.
        """
        cls.ins_cred = {"email": "instructor@bodhitree.com", "password": "instructor"}
        cls.ta_cred = {"email": "ta@bodhitree.com", "password": "ta"}
        cls.stu_cred = {"email": "student@bodhitree.com", "password": "student"}

    def get_documents_helper(self):
        url = reverse("document:document-list-documents", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        length = Document.objects.filter(chapter_id=1).count()
        self.assertEqual(len(response.data), length)

    def test_get_documents(self):
        """
        Ensure we can get all Docuemnts objects.
        """
        self.login(**self.ins_cred)
        self.get_documents_helper()
        self.logout()
        self.login(**self.ta_cred)
        self.get_documents_helper()
        self.logout()
        self.login(**self.stu_cred)
        self.get_documents_helper()
        self.logout()

    def get_documents_helper_section(self):
        url = reverse("document:document-list-documents-per-section", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        length = Document.objects.filter(section_id=1).count()
        self.assertEqual(len(response.data), length)

    def test_get_documents_per_section(self):
        """
        Ensure we can get all Docuemnts objects of section
        """
        self.login(**self.ins_cred)
        self.get_documents_helper_section()
        self.logout()
        self.login(**self.ta_cred)
        self.get_documents_helper_section()
        self.logout()
        self.login(**self.stu_cred)
        self.get_documents_helper_section()
        self.logout()

    def get_document_helper(self, doc_id):
        url = reverse(
            "document:document-retrieve-document",
            kwargs={"pk": doc_id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], doc_id)

    def test_get_document(self):
        """
        Ensure we can get one document object.
        """
        doc_id = 1
        self.login(**self.ins_cred)
        self.get_document_helper(doc_id)
        self.logout()
        self.login(**self.ta_cred)
        self.get_document_helper(doc_id)
        self.logout()
        self.login(**self.stu_cred)
        self.get_document_helper(doc_id)
        self.logout()

    def create_document_helper(self, title, status_code):
        doc_file_path = "main/test_data/doc/eye-of-the-tiger-workout.pdf"
        doc_content = open(doc_file_path, "rb").read()
        doc_content = b"doc_content"
        doc = BytesIO(doc_content)
        doc.name = "doc.pdf"
        data = {
            "chapter": 1,
            "section": "",
            "title": title,
            "doc_file": doc,
            "description": "This is the doc description",
        }
        url = reverse("document:document-create-document", args=[1])
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            return_data = response.data
            for k in ["created_on", "modified_on", "id", "doc_file", "section"]:
                return_data.pop(k)
            for k in ["doc_file", "section"]:
                data.pop(k)
            self.assertEqual(return_data, data)

    def test_create_document(self):
        """
        Ensure we can create a new 'document' object
        """
        self.client.login(**self.ins_cred)
        self.create_document_helper("document3", status.HTTP_201_CREATED)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.create_document_helper("document4", status.HTTP_201_CREATED)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.create_document_helper("document5", status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def update_documents_helper(self, title, status_code):
        document_file_path = "main/test_data/doc/eye-of-the-tiger-workout.pdf"
        document_content = open(document_file_path, "rb").read()
        _file = SimpleUploadedFile("doc.pdf", b"document_content")
        document1 = Document(
            title="document77",
            chapter_id=1,
            doc_file=_file,
        )
        document1.save()
        document_content = open(document_file_path, "rb").read()
        document_content = b"document_content"
        _file = SimpleUploadedFile("doc.pdf", document_content)
        data = {
            "title": title,
            "chapter": 1,
            "doc_file": _file,
            "description": "This is the doc description",
        }
        url = reverse(
            ("document:document-update-document"), kwargs={"pk": document1.id}
        )
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for k in ["created_on", "modified_on", "id", "doc_file", "section"]:
                return_data.pop(k)
            for k in ["doc_file"]:
                data.pop(k)
            self.assertEqual(return_data, data)

    def test_update_documents(self):
        """
        Ensure we can update an existing document object.
        """
        self.client.login(**self.ins_cred)
        self.update_documents_helper("document78", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.update_documents_helper("document79", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.update_documents_helper("document80", status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def partial_update_helper(self, title, status_code):
        document_file_path = "main/test_data/doc/eye-of-the-tiger-workout.pdf"
        document_content = open(document_file_path, "rb").read()
        _file = SimpleUploadedFile("doc.pdf", b"document_content")
        document1 = Document(
            title="document77",
            chapter_id=1,
            doc_file=_file,
        )
        document1.save()
        document_content = open(document_file_path, "rb").read()
        document_content = b"document_content"
        _file = SimpleUploadedFile("doc.pdf", document_content)
        data = {
            "title": title,
            "description": "This is the section description",
        }
        url = reverse(
            ("document:document-update-document"), kwargs={"pk": document1.id}
        )
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for k in [
                "created_on",
                "modified_on",
                "id",
                "doc_file",
                "section",
                "chapter",
            ]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_partial_update_document(self):
        """
        Ensure we can partially update an existing Document object.
        """
        self.client.login(**self.ins_cred)
        self.partial_update_helper("Document78", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.partial_update_helper("Document79", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.partial_update_helper("Document80", status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def delete_document_helper(self, title, status_code):
        document_file_path = "main/test_data/doc/eye-of-the-tiger-workout.pdf"
        document_content = open(document_file_path, "rb").read()
        document_content = b"document_content"
        _file = SimpleUploadedFile("doc.pdf", document_content)
        document1 = Document(
            title="document77",
            chapter_id=1,
            doc_file=_file,
        )
        document1.save()
        url = reverse(
            ("document:document-delete-document"), kwargs={"pk": document1.id}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        try:
            Document.objects.get(id=document1.id)
        except ObjectDoesNotExist:
            self.assertEqual(response.status_code, status_code)

    def test_delete_document(self):
        """
        Ensure we can delete an existing document object.
        """
        self.client.login(**self.ins_cred)
        self.delete_document_helper("document98", status.HTTP_204_NO_CONTENT)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.delete_document_helper("document99", status.HTTP_204_NO_CONTENT)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.delete_document_helper("document100", status.HTTP_403_FORBIDDEN)
        self.client.logout()
