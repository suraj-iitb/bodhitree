from django.urls import include, path
from rest_framework import routers

from .api import (
    AdvancedProgrammingAssignmentViewSet,
    AssignmentSectionViewSet,
    SimpleProgrammingAssignmentViewSet,
)


app_name = "programming_assignments"

router = routers.DefaultRouter()
router.register(r"simpleprogrammingassignment", SimpleProgrammingAssignmentViewSet)
router.register(r"advancedprogrammingassignment", AdvancedProgrammingAssignmentViewSet)
router.register(r"assignmentsection", AssignmentSectionViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
