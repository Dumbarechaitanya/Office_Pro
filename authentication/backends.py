from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from base.models import ResUsers


class ResUsersBackend(BaseBackend):
    """
    Custom Django authentication backend that authenticates against ResUsers (res_users table).
    Supports logging in with either username or email.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        identifier = str(username).strip()
        user = ResUsers.objects.filter(
            Q(username__iexact=identifier) | Q(email__iexact=identifier),
            is_active=True
        ).select_related('company', 'employee').first()

        if user and user.password_hash:
            if check_password(password, user.password_hash):
                return user

        return None

    def get_user(self, user_id):
        try:
            return ResUsers.objects.filter(is_active=True).select_related('company', 'employee').get(pk=user_id)
        except (ResUsers.DoesNotExist, ValueError, TypeError):
            return None
