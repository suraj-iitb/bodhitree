import logging
import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from registration.models import Profile, SubscriptionHistory
from utils import mixins as custom_mixins
from utils.pagination import StandardResultsSetPagination
from utils.permissions import (
    IsInstructorOrTA,
    IsInstructorOrTAOrReadOnly,
    IsInstructorOrTAOrStudent,
    IsOwner,
)
from utils.subscription import SubscriptionView
from utils.utils import CaseInsensitiveHeaderDictReader, get_course_folder

from .models import Announcement, Chapter, Course, CourseHistory, Page, Section
from .serializers import (
    AnnouncementSerializer,
    ChapterSerializer,
    CourseHistorySerializer,
    CourseSerializer,
    PageSerializer,
    SectionSerializer,
)


User = get_user_model()

logger = logging.getLogger(__name__)


class CourseViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    """ViewSet for `Course`."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsInstructorOrTAOrReadOnly,)
    pagination_class = StandardResultsSetPagination
    filterset_fields = (
        "owner__email",
        "code",
        "title",
        "is_published",
    )
    search_fields = (
        "owner__email",
        "code",
        "title",
        "is_published",
    )

    def _create_course_check(self, user):
        """Checks if the user can create a course.

        Args:
            user (User): `User` model object

        Returns:
            A bool value representing whether the user can create a course or not.

        Raises:
            `HTTP_403_FORBIDDEN`: Raised if:
                1. The course limit of the subscription is reached.
                2. `SubscriptionHistory.DoesNotExist` exception
        """
        try:
            if not SubscriptionView.is_course_limit_reached(user):
                return True

            error = "For user: `{}`, the limit of number of courses reached.".format(
                user
            )
            logger.warning(error)
            return Response(error, status.HTTP_403_FORBIDDEN)
        except SubscriptionHistory.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_403_FORBIDDEN)

    def _update_course_check(self, course_id, user):
        """Checks if the user can update a course.

        Args:
            course_id: Course id
            user (User): `User` model object

        Returns:
            A bool value representing whether the user can update a course or not.

        Raises:
            `HTTP_404_NOT_FOUND`: Raised by `Course.DoesNotExist` exception
            `HTTP_403_FORBIDDEN`: Raised if the subscription is not valid
        """
        try:
            course = Course.objects.select_related("owner").get(id=course_id)
        except Course.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        if SubscriptionView.has_valid_subscription(course.owner):
            return True

        error = "User: `{}` is not permitted to update the course: `{}`.".format(
            user, course
        )
        logger.warning(error)
        return Response(error, status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=["POST"])
    def create_course(self, request):
        """Adds a course.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created course data and status `HTTP_201_CREATED`.

        Raises:
            `HTTP_400_BAD_REQUEST`: Raised due to serialization errors
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrReadOnly` permission
                class
            HTTP_403_FORBIDDEN: Raised by:
                1. `IntegrityError` of the database
                2. `_create_course_check()` method
        """
        user = request.user
        check = self._create_course_check(user)
        if check is not True:
            return check

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            course_history = CourseHistory(
                user=user, course=serializer.instance, role="I", status="E"
            )
            course_history.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_course(self, request, pk):
        """Updates a course with id as pk

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with the updated course data and status `HTTP_200_OK`.

        Raises:
            `HTTP_400_BAD_REQUEST`: Raised due to serialization errors
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrReadOnly` permission
                class
            `HTTP_403_FORBIDDEN`: Raised by:
                1.  `IsInstructorOrTAOrReadOnly` permission class
                2. `IntegrityError` of the database
                3. `_update_course_check()` method
            HTTP_404_NOT_FOUND: Raise by `_update_course_check()` method
        """
        check = self._update_course_check(pk, request.user)
        if check is not True:
            return check

        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["DELETE"], permission_classes=[IsOwner])
    def delete_course(self, request, pk):
        """Deletes the course with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with no data and status HTTP_204_NO_CONTENT.

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsOwner` permission class
            `HTTP_403_FORBIDDEN`: Raised by `IsOwner` permission class
        """
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _store_file(self, request, course):
        """Helper function to store the attached file in the server.

        Args:
            request (Request): DRF `Request` object
            course (Course): `Course` model object

        Returns:
            Path on the server where file is stored.
        """
        directory = os.path.join(
            settings.MEDIA_ROOT, get_course_folder(course), "enrollment_files"
        )
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = (
            "students_enrolment-"
            + datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
            + ".csv"
        )
        file_path = os.path.join(directory, filename)

        with open(file_path, "wb") as f:
            for chunk in request.data["enrollment_file"].chunks():
                f.write(chunk)
        return file_path

    def _validate_and_get_extra_fields(self, header_fields):
        """Helper function to find extra header fields.

        Args:
            header_fields (list): Header fields in csv file (first row)

        Raises:
            KeyError: Raised if email or name is not present in the header

        Returns:
           A list of extra header fields.
        """
        if "email" not in header_fields:
            raise KeyError
        if "name" not in header_fields:
            raise KeyError

        extra_fields = header_fields
        extra_fields.remove("email")
        extra_fields.remove("name")
        return extra_fields

    def _clean_and_validate_student_data(self, student_data, header_fields):
        """Cleans and validates student data

        [extended_summary]

        Args:
            student_data ([type]): Studnet data in csv file (a row)
            header_fields ([type]): Header fields in csv file (first row)

        Raises:
            ValueError: Raised if email and/or name is not provided
            ValidationError: Invalid email

        Returns:
            Validated student data
        """
        for field in header_fields:
            if field == "":
                student_data.pop(field)
            else:
                student_data[field] = student_data[field].strip()

        student_email = student_data["email"]
        # checks for mandatory fields data
        if (not student_email) or (not student_data["name"]):
            raise ValueError

        # TODO: check for emptiness for any other field data

        # check for valid email
        try:
            validate_email(student_email)
        except ValidationError as e:
            raise ValidationError(e)

        return student_data

    def _handle_message(self, enrollment_stats):
        """Will be deleted as it will be handled in frontend"""
        msg = "##################################################################\n\n"
        msg += "USER ACCOUNTS STATUS\n\n"

        duplicate_email_set = enrollment_stats["duplicate_email_set"]
        if duplicate_email_set:
            msg += "{} user(s) are not processed due to more than one record in csv file.\
                 The users are:\n{}\n\n".format(
                len(duplicate_email_set), "\n".join(duplicate_email_set)
            )
        existing_users_count = enrollment_stats["existing_users_count"]
        if enrollment_stats["existing_users_count"]:
            msg += "{} user(s) accounts already exist.\n\n".format(existing_users_count)
        new_users_count = enrollment_stats["new_users_count"]
        if enrollment_stats["new_users_count"]:
            msg += "{} user(s) accounts newly created.\n\n".format(new_users_count)

        msg += "##################################################################\n\n"
        msg += "COURSE ENROLLMENT STATUS\n\n"

        existing_enrollments_count = enrollment_stats["existing_enrollments_count"]
        if existing_enrollments_count:
            msg += "{} user(s) already enrolled in this course.\n\n".format(
                existing_enrollments_count
            )
        pending_enrollments_count = enrollment_stats["pending_enrollments_count"]
        new_enrollments_count = enrollment_stats["new_enrollments_count"]
        if (
            enrollment_stats["pending_enrollments_count"]
            or enrollment_stats["new_enrollments_count"]
        ):
            msg += "{} user(s) newly enrolled in this course.\n\n".format(
                pending_enrollments_count + new_enrollments_count
            )

        return Response(msg, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def bulk_register_into_course(self, request, pk):
        """Bulk rgeister users from csv in a course with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk ([type]): Primary key of course

        Returns:
            A dictionary of enrollment stats.
        """
        try:
            course = Course.objects.get(id=pk)
        except Course.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        file_path = self._store_file(request, course)

        # TODO: premium checks

        student_list = []
        email_count = {}

        with open(file_path, "r") as f:
            reader = CaseInsensitiveHeaderDictReader(f, delimiter=",")
            header_fields = reader.fieldnames

            try:
                extra_fields = self._validate_and_get_extra_fields(header_fields)
                print(extra_fields)
            except KeyError as e:
                return (str(e), status.HTTP_404_NOT_FOUND)

            for student in reader:
                student_list.append(student)
                student_email = student["email"]
                email_count[student_email] = email_count.get(student_email, 0) + 1

        duplicate_email_set = set()
        new_user_list = list()
        existing_users_count = 0

        new_enrollment_list = list()
        existing_enrollments_count = 0
        pending_enrollments_count = 0

        for student in student_list:
            try:
                student = self._clean_and_validate_student_data(student, header_fields)
            except ValueError:
                return ({}, status.HTTP_404_NOT_FOUND)
            except ValidationError:
                return ({}, status.HTTP_404_NOT_FOUND)

            student_email = student["email"]
            if email_count[student_email] > 1:
                duplicate_email_set.add(student_email)
                continue

            # `User` and `CourseHistory` object creation for `bulk_create()` method
            try:
                user = User.objects.get(email=student_email)
                existing_users_count += 1

                try:
                    course_history = CourseHistory.objects.get(user=user, course=course)
                    if course_history.status == "E":
                        existing_enrollments_count += 1
                    else:
                        course_history.status = "E"
                        course_history.save()
                        pending_enrollments_count += 1
                except CourseHistory.DoesNotExist:
                    course_history = CourseHistory(user=user, course=course, status="E")
                    new_enrollment_list.append(course_history)
            except User.DoesNotExist:
                user = User(
                    email=student_email,
                    full_name=student["name"],
                    is_active=True,
                )
                new_user_list.append(user)
                course_history = CourseHistory(user=user, course=course, status="E")
                new_enrollment_list.append(course_history)

        # Bulk creation for `User`
        created_user_list = User.objects.bulk_create(new_user_list)

        # Bulk creation for  `CourseHistory`
        CourseHistory.objects.bulk_create(new_enrollment_list)

        # Bulk creation for  `Profile`
        Profile.objects.bulk_create([Profile(user=user) for user in created_user_list])
        # TODO: handle roll no mismatch if profile exists

        # TODO: Bulk creation for CourseBatchTag & CourseBatchTagHistory

        # TODO: send email

        enrollment_stats = dict()
        enrollment_stats["duplicate_email_set"] = duplicate_email_set
        enrollment_stats["existing_users_count"] = existing_users_count
        enrollment_stats["new_users_count"] = len(new_user_list)
        enrollment_stats["existing_enrollments_count"] = existing_enrollments_count
        enrollment_stats["pending_enrollments_count"] = pending_enrollments_count
        enrollment_stats["new_enrollments_count"] = len(new_enrollment_list)

        return self._handle_message(enrollment_stats)


class CourseHistoryViewSet(viewsets.GenericViewSet, custom_mixins.IsRegisteredMixin):
    """ViewSet for `CourseHistory`."""

    queryset = CourseHistory.objects.all()
    serializer_class = CourseHistorySerializer
    permission_classes = (IsInstructorOrTAOrStudent,)
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=["POST"])
    def create_course_history(self, request):
        """Adds a course history for a course

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created course history data and status
            `HTTP_201_CREATED`.

        Raises:
            `HTTP_400_BAD_REQUEST`: Raised due to serialization errors
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrStudent` permission
                class
            `HTTP_403_FORBIDDEN`: Raised by `IntegrityError` of the database
            `HTTP_404_NOT_FOUND`: Raised by `Course.DoesNotExist` exception
        """
        course_id = request.data["course"]
        try:
            Course.objects.get(id=course_id)
        except Course.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"])
    def list_course_histories(self, request, pk):
        """Gets all the course history in the course with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with all the course histories data and status `HTTP_200_OK`.

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrStudent` permission
                class
            `HTTP_403_FORBIDDEN`: Raised by `_is_registered()` method
            `HTTP_404_NOT_FOUND`: Raised by `Course.DoesNotExist` exception
        """
        try:
            Course.objects.get(id=pk)
        except Course.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        # This is specifically done during list all course histories (not during
        # retrieval of a course history) because it can't be handled by
        # `IsInstructorOrTAOrStudent` permission class.
        check = self._is_registered(pk, request.user)
        if check is not True:
            return check

        course_histories = CourseHistory.objects.filter(course_id=pk)
        page = self.paginate_queryset(course_histories)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(course_histories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_course_history(self, request, pk):
        """Gets the course history with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course history id

        Returns:
            `Response` with the course history data and status `HTTP_200_OK`.

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrStudent` permission
                class
            `HTTP_403_FORBIDDEN`: Raised by `IsInstructorOrTAOrStudent` permission class
            `HTTP_404_NOT_FOUND`: Raised by `get_object()` method
        """
        course_history = self.get_object()
        serializer = self.get_serializer(course_history)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"], permission_classes=[IsOwner])
    def update_course_history(self, request, pk):
        """Updates the course history with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course history id

        Returns:
            `Response` with the updated course history data and status `HTTP_200_OK`.

        Raises:
            `HTTP_400_BAD_REQUEST`: Raised due to serialization errors
            `HTTP_401_UNAUTHORIZED`: Raised by `IsOwner` permission class
            `HTTP_403_FORBIDDEN`: Raised by:
                1. `IsOwner` permission class
                2. `IntegrityError` of the database
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        course_history = self.get_object()
        serializer = self.get_serializer(
            course_history, data=request.data, partial=True
        )
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class ChapterViewSet(viewsets.GenericViewSet, custom_mixins.ChapterorPageMixin):
    """Viewset for `Chapter`."""

    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = (IsInstructorOrTA,)

    @action(detail=False, methods=["POST"])
    def create_chapter(self, request):
        return self.create(request)

    @action(detail=True, methods=["GET"])
    def list_chapters(self, request, pk):
        return self.list(request, pk, Chapter)

    @action(detail=True, methods=["GET"])
    def retrieve_chapter(self, request, pk):
        return self.retrieve(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_chapter(self, request, pk):
        return self.update(request, pk)

    @action(detail=True, methods=["DELETE"])
    def delete_chapter(self, request, pk):
        return self._delete(request, pk)


class SectionViewSet(viewsets.GenericViewSet, custom_mixins.IsRegisteredMixin):
    """Viewset for `Section`."""

    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = (IsInstructorOrTA,)

    @action(detail=False, methods=["POST"])
    def create_section(self, request):
        """Adds a section to the chapter.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created section data and status HTTP_201_CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by:
                1. `_is_instructor_or_ta()` permission class
                2. `IntegrityError` of the database
            HTTP_404_NOT_FOUND: Raised if the chapter does not exist
        """
        chapter_id = request.data["chapter"]

        try:
            chapter = Chapter.objects.get(id=chapter_id)
        except Chapter.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)
        course_id = chapter.course_id

        # This is specifically done during section creation (not during updation or
        # deletion) because it can't be handled by `IsInstructorOrTA` permission class
        check = self._is_instructor_or_ta(course_id, request.user)
        if check is not True:
            return check

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"])
    def list_sections(self, request, pk):
        """Gets all the sections in the chapter with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Chapter id

        Returns:
            `Response` with all the sections data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised if the chapter does not exist
        """
        try:
            chapter = Chapter.objects.get(id=pk)
        except Chapter.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)
        course_id = chapter.course_id

        # This is specifically done during list all sections (not during retrieval of
        # a section) because it can't be handled by `IsInstructorOrTA` permission class.
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check

        sections = Section.objects.filter(chapter_id=pk)
        serializer = self.get_serializer(sections, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_section(self, request, pk):
        """Gets the section with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Section id

        Returns:
            `Response` with the section data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        section = self.get_object()
        serializer = self.get_serializer(section)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_section(self, request, pk):
        """Updates the section with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Section id

        Returns:
            `Response` with the updated section data and status HTTP_200_OK.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by
                1. `IsInstructorOrTA` permission class
                2. `IntegrityError` of the database
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        section = self.get_object()
        serializer = self.get_serializer(section, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["DELETE"])
    def delete_section(self, request, pk):
        """Deletes the section with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Section id

        Returns:
            `Response` with no data and status HTTP_204_NO_CONTENT.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        section = self.get_object()
        section.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PageViewSet(viewsets.GenericViewSet, custom_mixins.ChapterorPageMixin):
    """Viewset for `Page`."""

    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (IsInstructorOrTA,)

    @action(detail=False, methods=["POST"])
    def create_page(self, request):
        return self.create(request)

    @action(detail=True, methods=["GET"])
    def list_pages(self, request, pk):
        return self.list(request, pk, Page)

    @action(detail=True, methods=["GET"])
    def retrieve_page(self, request, pk):
        return self.retrieve(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_page(self, request, pk):
        return self.update(request, pk)

    @action(detail=True, methods=["DELETE"])
    def delete_page(self, request, pk):
        return self._delete(request, pk)


class AnnouncementViewSet(viewsets.GenericViewSet, custom_mixins.ChapterorPageMixin):
    """Viewset for `Announcement`."""

    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = (IsInstructorOrTA,)

    @action(detail=False, methods=["POST"])
    def create_announcement(self, request):
        return self.create(request)

    @action(detail=True, methods=["GET"])
    def list_announcements(self, request, pk):
        return self.list(request, pk, Announcement)

    @action(detail=True, methods=["GET"])
    def retrieve_announcement(self, request, pk):
        return self.retrieve(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_announcement(self, request, pk):
        return self.update(request, pk)

    @action(detail=True, methods=["DELETE"])
    def delete_announcement(self, request, pk):
        return self._delete(request, pk)
