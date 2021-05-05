import logging

from dateutil.relativedelta import relativedelta
from django.utils import timezone

from course.models import Course
from registration.models import SubscriptionHistory


logger = logging.getLogger(__name__)


class SubscriptionView:
    """View for various checks of a user subscription"""

    @classmethod
    def _is_subscription_expired(cls, start_date, duration):
        """Checks if a user subscription is expired or not.

        Args:
            start_date (datetime): Start date of subscription
            duration (int): Duration of subscription

        Returns:
            A bool value denoting if a user subscription is expired or not.
        """
        # TODO: Correct timezone
        end_date = start_date + relativedelta(months=duration)
        if timezone.now() <= end_date:
            return False
        return True

    @classmethod
    def has_valid_subscription(cls, user):
        """Checks if a user has a subscription and it is valid or not.

        Args:
            user (User): `User` model intstance

        Returns:
            A bool value denoting if a user has a valid subscription or not.
        """
        try:
            subscription_history = SubscriptionHistory.objects.get(user=user)
        except SubscriptionHistory.DoesNotExist as e:
            logger.exception(e)
            return False

        if not cls._is_subscription_expired(
            subscription_history.start_date, subscription_history.duration
        ):
            return True
        return False

    @classmethod
    def is_course_limit_reached(cls, user):
        """Checks if the subscription course limit is exhausted for a user.

        Args:
            user (User): `User` model intstance

        Returns:
            A bool value denoting if subscription course limit is exhausted for a
            user or not.

        Raises:
            SubscriptionHistory.DoesNotExist: Raised if subscription history does not
                exist for a user.
        """
        no_of_courses = Course.objects.filter(owner=user).count()
        try:
            subscription_history = SubscriptionHistory.objects.select_related(
                "subscription"
            ).get(user=user)
        except SubscriptionHistory.DoesNotExist as e:
            logger.exception(e)
            raise
        if (
            no_of_courses < subscription_history.subscription.no_of_courses
            and not cls._is_subscription_expired(
                subscription_history.start_date, subscription_history.duration
            )
        ):
            return False
        return True
