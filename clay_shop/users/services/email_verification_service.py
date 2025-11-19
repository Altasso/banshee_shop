import logging

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from users.models import User

logger = logging.getLogger(__name__)


class EmailVerificationService:
    @staticmethod
    def generate_verification_link(user: User) -> str:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        relative_url = reverse("email-verify", kwargs={"uidb64": uid, "token": token})
        return f"{settings.SITE_URL}{relative_url}"

    @staticmethod
    def verify_email(uidb64: str, token: str) -> tuple[bool, str]:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return False, "Неверная ссылка"

        if user.is_verified:
            return True, "Email уже подтвержден"

        if not default_token_generator.check_token(user, token):
            return False, "Ссылка устарела"

        user.is_verified = True
        user.save(update_fields=["is_verified"])

        logger.info(f"User {user.email} verified")
        return True, "Email успешно подтвержден"
