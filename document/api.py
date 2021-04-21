from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from course.models import Chapter, Course, Section
from utils.drf_utils import IsInstructorOrTA
from utils.utils import check_course_registration, is_instructor_or_ta

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.GenericViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = (IsInstructorOrTA,)
    filterset_fields = (
        "chapter__title",
        "section__title",
        "title",
    )
    search_fields = (
        "chapter__title",
        "section__title",
        "title",
    )
    ordering_fields = ("id",)

    def _checks(self, course_id, chapter_id, user):
        """To check if the user is registered in a given course"""
        try:
            Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            data = {
                "error": "Course with id: {} does not exist".format(course_id),
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        if not check_course_registration(course_id, user):
            data = {
                "error": "User: {} not registered in course with id: {}".format(
                    user, course_id
                ),
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        try:
            Chapter.objects.get(id=chapter_id)
        except Chapter.DoesNotExist:
            data = {
                "error": "Chapter with id: {} does not exist".format(chapter_id),
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        return True

    @action(detail=True, methods=["POST"])
    def create_document(self, request, pk):
        """Add a document to a chapter/section with primary key as pk"""
        user = request.user
        doc = request.data
        if doc["section"] != "" and doc["chapter"] != "":
            data = {
                "Validation error": "Both chapter and section fields cannot be given"
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        if doc["section"] == "" and doc["chapter"] == "":
            data = {
                "Validation error": """Atleast one of
                 chapter and section fields must be given"""
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        if doc["chapter"] == "":
            section_id = doc["section"]
            chapter_id = Section.objects.get(id=section_id).chapter_id
        else:
            chapter_id = doc["chapter"]
        course_id = Chapter.objects.get(id=chapter_id).course_id
        instructor_or_ta = is_instructor_or_ta(course_id, user)
        if not instructor_or_ta:
            data = {
                "error": "User: {} is not instructor/ta of course with id: {}".format(
                    user, course_id
                ),
            }
            return Response(data, status.HTTP_403_FORBIDDEN)
        check = self._checks(course_id, chapter_id, request.user)
        if check is True:
            serializer = self.get_serializer(data=doc)
            serializer.is_valid()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return check

    @action(detail=True, methods=["GET"])
    def list_documents(self, request, pk):
        """Get all documents of a chapter with primary key as pk"""
        chapter_id = Chapter.objects.get(id=pk).id
        course_id = Chapter.objects.get(id=chapter_id).course.id
        check = self._checks(course_id, chapter_id, request.user)
        if check is True:
            documents = Document.objects.filter(chapter_id=pk)
            serializer = self.get_serializer(documents, many=True)
            return Response(serializer.data)
        return check

    @action(detail=True, methods=["GET"])
    def retrieve_document(self, request, pk):
        """Get a document with primary key as pk"""
        doc = self.get_object()
        if doc.chapter_id is None:
            section_id = doc.section_id
            chapter_id = Section.objects.get(id=section_id).chapter_id
        else:
            chapter_id = doc.chapter_id
        course_id = Chapter.objects.get(id=chapter_id).course_id
        check = self._checks(course_id, chapter_id, request.user)
        if check is True:
            serializer = self.get_serializer(doc)
            return Response(serializer.data)
        return check

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_document(self, request, pk):
        """Update document with primary key as pk"""
        document = self.get_object()
        if document.chapter_id is None:
            section_id = document.section_id
            chapter_id = Section.objects.get(id=section_id).chapter_id
        else:
            chapter_id = document.chapter_id
        course_id = Chapter.objects.get(id=chapter_id).course_id
        check = self._checks(course_id, chapter_id, request.user)
        if check is True:
            if document.chapter_id is not None and document.section_id is not None:
                data = {
                    "Validation error": """Both chapter and section
                     fields cannot be empty"""
                }
                return Response(data, status.HTTP_400_BAD_REQUEST)
            if document.chapter_id is None and document.section_id is None:
                data = {
                    "Validation error": """Atleast one of
                    chapter and section fields must be given"""
                }
                return Response(data, status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(document, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

        return check

    @action(detail=True, methods=["DELETE"])
    def delete_document(self, request, pk):
        """Delete document with primary key as pk"""
        document = self.get_object()
        if document.chapter_id is None:
            section_id = document.section_id
            chapter_id = Section.objects.get(id=section_id).chapter_id
        else:
            chapter_id = document.chapter_id
        course_id = Chapter.objects.get(id=chapter_id).course_id
        check = self._checks(course_id, chapter_id, request.user)
        if check is True:
            document.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return check
