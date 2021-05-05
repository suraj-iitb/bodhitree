import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from course.models import Chapter, Section
from utils import mixins as custom_mixins
from utils.permissions import IsInstructorOrTA
from utils.utils import check_is_instructor_or_ta

from .models import Document
from .serializers import DocumentSerializer


logger = logging.getLogger(__name__)


class DocumentViewSet(
    viewsets.GenericViewSet,
    custom_mixins.IsRegisteredMixins,
):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = (IsInstructorOrTA,)

    @action(detail=False, methods=["POST"])
    def create_document(self, request):
        """Adds a document to the chapter/section

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created document data and status HTTP_201_CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Raised by:
                1. `is_valid()` method of the serializer
                2. If both or none section/chapter is provided
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by:
                1. If the user is not the instructor/ta of the course
                2. `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by:
                1. `_is_registered()` method
                2. Chapter/Section does not exist
        """
        user = request.user
        request_data = request.data

        # Validation logic such that only chapter/section is provided
        if request_data["section"] != "" and request_data["chapter"] != "":
            data = {"error": "Both chapter and section fields cannot be given."}
            logger.error(data["error"])
            return Response(data, status.HTTP_400_BAD_REQUEST)
        if request_data["section"] == "" and request_data["chapter"] == "":
            data = {"error": "Atleast one of chapter or section fields must be given"}
            logger.error(data["error"])
            return Response(data, status.HTTP_400_BAD_REQUEST)
        ##############################################################

        # Finds course id
        if request_data["chapter"] == "":
            section_id = request_data["section"]
            try:
                chapter_id = (
                    Section.objects.select_related("chapter")
                    .get(id=section_id)
                    .chapter.id
                )
            except Section.DoesNotExist as e:
                logger.exception(e)
                Response(e, status.HTTP_404_NOT_FOUND)
        else:
            chapter_id = request_data["chapter"]
        try:
            course_id = (
                Chapter.objects.select_related("course").get(id=chapter_id).course.id
            )
        except Chapter.DoesNotExist as e:
            logger.exception(e)
            Response(e, status.HTTP_404_NOT_FOUND)
        #################

        check = self._is_registered(course_id, user)
        if check is not True:
            return check

        # This is specifically done during document creation (not during updation or
        # deletion) because it can't be handled by IsInstructorOrTA permission class
        if not check_is_instructor_or_ta(course_id, user):
            data = {
                "error": "User: {} is not the instructor/ta of the "
                "course with id: {}".format(user, course_id),
            }
            logger.warning(data["error"])
            return Response(data, status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"])
    def list_chapter_documents(self, request, pk):
        """Gets all the documents in the chapter with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): chapter id

        Returns:
            `Response` with all the document data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered_using_chapter_id()` method
        """
        check, _ = self._is_registered_using_chapter_id(pk, request.user)
        if check is not True:
            return check

        documents = Document.objects.filter(chapter_id=pk)
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def list_section_documents(self, request, pk):
        """Gets all the documents in the section with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): section id

        Returns:
            `Response` with all the documents data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered_using_chapter_id()` method
        """
        check, _ = self._is_registered_using_section_id(pk, request.user)
        if check is not True:
            return check

        documents = Document.objects.filter(section_id=pk)
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_document(self, request, pk):
        """Gets the document with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): document id

        Returns:
            `Response` with the document data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by:
                1. `_is_registered_using_chapter_id()` method
                2. `_is_registered_using_section_id()` method
        """
        user = request.user
        document = self.get_object()
        if document.chapter_id is None:
            check, course_id = self._is_registered_using_section_id(
                document.section_id, user
            )
        else:
            check, course_id = self._is_registered_using_chapter_id(
                document.chapter_id, user
            )
        if check is not True:
            return check

        serializer = self.get_serializer(document)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_document(self, request, pk):
        """Updates the document with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): document id

        Returns:
            `Response` with the updated document data and status HTTP_200_OK.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by:
                1. `_is_registered_using_chapter_id()` method
                2. `_is_registered_using_section_id()` method
        """
        user = request.user
        document = self.get_object()
        if document.chapter_id is None:
            check, course_id = self._is_registered_using_section_id(
                document.section_id, user
            )
        else:
            check, course_id = self._is_registered_using_chapter_id(
                document.chapter_id, user
            )
        if check is not True:
            return check

        serializer = self.get_serializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["DELETE"])
    def delete_document(self, request, pk):
        """Deletes the document with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): document id

        Returns:
            `Response` with no data and status HTTP_204_NO_CONTENT.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        user = request.user
        document = self.get_object()
        if document.chapter_id is None:
            check, course_id = self._is_registered_using_section_id(
                document.section_id, user
            )
        else:
            check, course_id = self._is_registered_using_chapter_id(
                document.chapter_id, user
            )
        if check is not True:
            return check

        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
