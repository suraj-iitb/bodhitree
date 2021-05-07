import logging

from rest_framework import viewsets
from rest_framework.decorators import action

from utils import mixins as custom_mixins
from utils.permissions import IsInstructorOrTA

from .models import Document
from .serializers import DocumentSerializer


logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.GenericViewSet, custom_mixins.ContentMixin):
    """Viewset for `Document`."""

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = (IsInstructorOrTA,)

    @action(detail=False, methods=["POST"])
    def create_document(self, request):
        return self.create_content(request)

    @action(detail=True, methods=["GET"])
    def list_chapter_documents(self, request, pk):
        return self.list_chapter_content(request, pk, Document)

    @action(detail=True, methods=["GET"])
    def list_section_documents(self, request, pk):
        return self.list_section_content(request, pk, Document)

    @action(detail=True, methods=["GET"])
    def retrieve_document(self, request, pk):
        return self.retrieve_content(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_document(self, request, pk):
        return self.update_content(request, pk)

    @action(detail=True, methods=["DELETE"])
    def delete_document(self, request, pk):
        return self.delete_content(request, pk)
